// compile from 64bit vs developer windows: cl /EHsc read-proc-env.cpp

// this just makes things simpler. from a 32-bit process, you can normally read only from 32-bit processes (even on 64-bit os)
// (there are apis you can use to read from 64 bit processes, but i just kept it simple)
static_assert(sizeof(void*) == 8, "must compile as x64");

#include <iostream>
#include <string>
#include <sstream>
#include <Windows.h>

struct UNICODE_STRING {
	USHORT Length;
	USHORT MaximumLength;
	PWSTR  Buffer;
};

class Win32Error : public std::exception
{
public:
	Win32Error(const char * const reason)
	{
		DWORD err = GetLastError();

		LPSTR message_buffer = NULL;
		size_t size = FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
			NULL, err, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&message_buffer, 0, NULL);
		if (size == 0) throw std::runtime_error((std::string)"Win32Error ctor: Error calling FormatMessageA for " + std::to_string(err));

		msg = (std::string)"Win32Error: " = std::to_string(err) + " - " + message_buffer + " (" + reason + ")";

		HLOCAL ret = LocalFree(message_buffer);
		if (ret != NULL) throw std::runtime_error((std::string)"Win32Error ctor: Error calling LocalFree for " + std::to_string((uint64_t)message_buffer));
	}

	virtual char const* what() const override
	{
		return msg.c_str();
	}

private:
	std::string msg;
};

class Process
{
public:
	Process(DWORD dwDesiredAccess, DWORD pid)
	{
		this->pid = pid;
		this->hProcess = OpenProcess(dwDesiredAccess, FALSE, pid);
		if (this->hProcess == NULL) throw Win32Error("OpenProcess failed");
	}

	void ReadMemory(LPCVOID lpBaseAddress, LPVOID lpBuffer, SIZE_T nSize, SIZE_T* lpNumberOfBytesRead, const char * const operatioTag = NULL)
	{
		BOOL ret = ReadProcessMemory(hProcess, lpBaseAddress, lpBuffer, nSize, lpNumberOfBytesRead);
		std::string tag = operatioTag ? (std::string)" (" + operatioTag + ")" : "";
		if (!ret) throw Win32Error(((std::string)"ReadProcessMemory failed" + tag).c_str());
	}

	~Process()
	{
		CloseHandle(hProcess);
	}

	DWORD pid = 0;
	HANDLE hProcess = NULL;
};

unsigned int safe_atoi(const char* str)
{
	if (str == NULL) throw std::runtime_error("safe_atoi: str is null");
	size_t len = strlen(str);

	unsigned int ret = 0, ret_prev;
	while (char c = *str++)
	{
		if (c < '0' || c > '9') throw std::runtime_error((std::string)"safe_atoi: invalid digit '" + c + "'");
		int n = c - '0';
		ret_prev = ret;
		ret = ret * 10 + n;
		if ((ret - n) / 10 != ret_prev) throw std::runtime_error("safe_atoi: str out of range");
	}
	return ret;
}

void throw_if_nt_error(NTSTATUS err, const char * const reason)
{
	if (err != 0)
	{
		std::stringstream stream;
		stream << "nt error: '0x" << std::hex << std::uppercase << err << "' - " << reason;
		throw std::runtime_error(stream.str());
	}
}

PVOID get_peb_address(Process& p)
{
	// PROCESS_BASIC_INFORMATION struct for 64-bit os (also for 32-bit processes)
	struct PROCESS_BASIC_INFORMATION  {
		PVOID Reserved1;
		PVOID PebBaseAddress;
		PVOID Reserved2[2];
		ULONG_PTR UniqueProcessId;
		PVOID Reserved3;
	};
	PROCESS_BASIC_INFORMATION pbi = {};

	// NtQueryInformationProcess decleration
	typedef NTSTATUS(NTAPI* _NtQueryInformationProcess)(
		IN HANDLE ProcessHandle,
		ULONG ProcessInformationClass,
		OUT PVOID ProcessInformation,
		IN ULONG ProcessInformationLength,
		OUT PULONG ReturnLength OPTIONAL
		);

	// call
	_NtQueryInformationProcess query = (_NtQueryInformationProcess)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtQueryInformationProcess");
	NTSTATUS nt_err = query(p.hProcess, 0, &pbi, sizeof(pbi), NULL);
	throw_if_nt_error(nt_err, "NtQueryInformationProcess failed");

	return pbi.PebBaseAddress;
}

int _main(int argc, char* argv[])
{
	if (argc != 2)
	{
		std::cout << "usage: " << argv[0] << " <pid>" << std::endl;
		return 1;
	}

	DWORD pid = safe_atoi(argv[1]);

	Process p(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, pid);

	// use WinDbg "dt ntdll!_PEB" command to find the ProcessParameters offset
	const DWORD OFFSET_ProcessParameters = 0x020; // relateive to PEB
	const DWORD OFFSET_CommandLine       = 0x070; // relateive to ProcessParameters
	const DWORD OFFSET_Environment       = 0x080; // relateive to ProcessParameters
	const DWORD OFFSET_EnvironmentSize   = 0x3f0; // relateive to ProcessParameters

	PVOID peb_remote_ptr = get_peb_address(p);

	// read the ProcessParameters pointer from the PEB
	PVOID pparams_remote_ptr;
	p.ReadMemory((char*)peb_remote_ptr + OFFSET_ProcessParameters, &pparams_remote_ptr, sizeof(pparams_remote_ptr), NULL, "pparams_remote_ptr");

	// read the CommandLine UNICODE_STRING struct from the ProcessParameters
	UNICODE_STRING command_line_us;
	p.ReadMemory((char*)pparams_remote_ptr + OFFSET_CommandLine, &command_line_us, sizeof(command_line_us), NULL, "command_line_us");
	// read the CommandLine string from the UNICODE_STRING
	PWSTR command_line = new WCHAR[command_line_us.MaximumLength];
	p.ReadMemory(command_line_us.Buffer, command_line, command_line_us.MaximumLength, NULL, "command_line");

	// read the Environment block pointer from the ProcessParameters
	PVOID environment_remote_ptr;
	p.ReadMemory((char*)pparams_remote_ptr + OFFSET_Environment, &environment_remote_ptr, sizeof(environment_remote_ptr), NULL, "environment_remote_ptr");

	// read the EnvironmentSize value from the ProcessParameters
	UINT64 environment_size;
	p.ReadMemory((char*)pparams_remote_ptr + OFFSET_EnvironmentSize, &environment_size, sizeof(environment_size), NULL, "environment_size");

	// read the Environment buffer from pointer
	WCHAR* environment = new WCHAR[environment_size];
	p.ReadMemory(environment_remote_ptr, environment, environment_size, NULL, "environment");

	// prepare the environment buffer to be printed
	// (each variable=value is stored as a null terminated string, and 2 nulls mark the end of the block)
	int i = 0;
	while (environment[i] != NULL || environment[i+1] != NULL) // till the end of the block
	{
		if (environment[i] == NULL)
			environment[i] = L'\n'; // replace nulls with new line
		++i;
	}

	std::wcout
		<< "PID: " << pid << std::endl
		<< "============= " << std::endl
		<< "command_line: " << command_line << std::endl
		<< "environment:" << std::endl << environment << std::endl
		<< "==========" << std::endl;

	delete command_line;
	delete environment;

	return 0;
}

int main(int argc, char* argv[])
{
	try
	{
		return _main(argc, argv);
	}
	catch (std::exception& e)
	{
		std::cout << "ERROR: " << e.what();
		return 1;
	}
}
