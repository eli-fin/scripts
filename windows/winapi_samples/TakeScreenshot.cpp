#include <iostream>
#include <fstream>
#include <Windows.h>

struct ByteArray
{
	int size;
	void* buffer;
};

ByteArray getBitmap(double);
PBITMAPINFO CreateBitmapInfoStruct(HBITMAP);
ByteArray CreateBMPFile(PBITMAPINFO, HBITMAP, HDC);

void main()
{
	double scale = 1;
	char* filename = "file.bmp";
	ByteArray bArr = getBitmap(.6);
	std::ofstream(filename, std::ios::binary).write((char*)bArr.buffer, bArr.size);
	delete bArr.buffer;
}

// Get bytes of the BMP file according to scale
ByteArray getBitmap(double scale)
{
	// Get screen device context
	HDC hdcSource = GetDC(NULL);
	// Create a memory device context (because bitmaps can only be selected into memory device contexts)
	HDC hdcMemory = CreateCompatibleDC(hdcSource);
	
	// Get screen XY
	int capX = GetDeviceCaps(hdcSource, HORZRES);
	int capY = GetDeviceCaps(hdcSource, VERTRES);
	
	// Create bitmat object compatible with screen screen size * scale
	HBITMAP hBitmap = CreateCompatibleBitmap(hdcSource, capX*scale, capY*scale);
	// Connect bitmap to device context
	SelectObject(hdcMemory, hBitmap);
	
	// Copy screen device to memory device
	StretchBlt(hdcMemory, 0, 0, capX*scale, capY*scale, hdcSource, 0, 0, capX, capY, SRCCOPY);

	// Get info struct
	PBITMAPINFO inf = CreateBitmapInfoStruct(hBitmap);
	ByteArray bytes = CreateBMPFile(inf, hBitmap, hdcSource);
	
	// Free resources
	DeleteDC(hdcSource);
	DeleteDC(hdcMemory);

	return bytes;
}

// Create the info struct for the bitmap
PBITMAPINFO CreateBitmapInfoStruct(HBITMAP hBmp)
{
	BITMAP bmp;
	PBITMAPINFO pbmi;
	WORD    cClrBits;

	// Retrieve the bitmap color format, width, and height.  
	if (!GetObject(hBmp, sizeof(BITMAP), (LPSTR)&bmp))
		std::cout << "Error GetObject";

	// Convert the color format to a count of bits.  
	cClrBits = (WORD)(bmp.bmPlanes * bmp.bmBitsPixel);
	if (cClrBits == 1)
		cClrBits = 1;
	else if (cClrBits <= 4)
		cClrBits = 4;
	else if (cClrBits <= 8)
		cClrBits = 8;
	else if (cClrBits <= 16)
		cClrBits = 16;
	else if (cClrBits <= 24)
		cClrBits = 24;
	else cClrBits = 32;

	// Allocate memory for the BITMAPINFO structure. (This structure  
	// contains a BITMAPINFOHEADER structure and an array of RGBQUAD  
	// data structures.)  

	if (cClrBits < 24)
		pbmi = (PBITMAPINFO)LocalAlloc(LPTR,
			sizeof(BITMAPINFOHEADER) +
			sizeof(RGBQUAD) * (1 << cClrBits));

	// There is no RGBQUAD array for these formats: 24-bit-per-pixel or 32-bit-per-pixel 

	else
		pbmi = (PBITMAPINFO)LocalAlloc(LPTR,
			sizeof(BITMAPINFOHEADER));

	// Initialize the fields in the BITMAPINFO structure.  

	pbmi->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
	pbmi->bmiHeader.biWidth = bmp.bmWidth;
	pbmi->bmiHeader.biHeight = bmp.bmHeight;
	pbmi->bmiHeader.biPlanes = bmp.bmPlanes;
	pbmi->bmiHeader.biBitCount = bmp.bmBitsPixel;
	if (cClrBits < 24)
		pbmi->bmiHeader.biClrUsed = (1 << cClrBits);

	// If the bitmap is not compressed, set the BI_RGB flag.  
	pbmi->bmiHeader.biCompression = BI_RGB;

	// Compute the number of bytes in the array of color  
	// indices and store the result in biSizeImage.  
	// The width must be DWORD aligned unless the bitmap is RLE 
	// compressed. 
	pbmi->bmiHeader.biSizeImage = ((pbmi->bmiHeader.biWidth * cClrBits + 31) & ~31) / 8
		* pbmi->bmiHeader.biHeight;
	// Set biClrImportant to 0, indicating that all of the  
	// device colors are important.  
	pbmi->bmiHeader.biClrImportant = 0;
	return pbmi;
}

// Create the BMP file bites according to header and bitmap
// (pass HDC used to create the bitmap)
ByteArray CreateBMPFile(PBITMAPINFO pbi, HBITMAP hBMP, HDC hDC)
{
	ByteArray result;

	BITMAPFILEHEADER hdr;       // bitmap file-header  
	PBITMAPINFOHEADER pbih;     // bitmap info-header  
	char* lpBits;              // memory pointer  

	pbih = &pbi->bmiHeader;
	lpBits = new char[pbi->bmiHeader.biSizeImage];

	// Retrieve the color table (RGBQUAD array) and the bits  
	// (array of palette indices) from the DIB. 
	if (!GetDIBits(hDC, hBMP, 0, (WORD)pbih->biHeight, lpBits, pbi, DIB_RGB_COLORS))
	{
		std::cout << "Error GetDIBits";
	}

	hdr.bfType = 0x4d42;        // 0x42 = "B" 0x4d = "M"  
								// Compute the size of the entire file.  
	hdr.bfSize = (DWORD)(sizeof(BITMAPFILEHEADER) +
		pbih->biSize + pbih->biClrUsed
		* sizeof(RGBQUAD) + pbih->biSizeImage);
	hdr.bfReserved1 = 0;
	hdr.bfReserved2 = 0;

	// Compute the offset to the array of color indices.  
	hdr.bfOffBits = (DWORD) sizeof(BITMAPFILEHEADER) +
		pbih->biSize + pbih->biClrUsed
		* sizeof(RGBQUAD);

	int bufSize =
		sizeof(BITMAPFILEHEADER) +
		(sizeof(BITMAPINFOHEADER) + pbih->biClrUsed * sizeof(RGBQUAD)) +
		pbih->biSizeImage;
	char* buf = new char[bufSize];
	char* bufP = buf;
	memcpy(bufP, &hdr, sizeof(BITMAPFILEHEADER));
	bufP += sizeof(BITMAPFILEHEADER);
	memcpy(bufP, pbih, sizeof(BITMAPINFOHEADER) + pbih->biClrUsed * sizeof(RGBQUAD));
	bufP += sizeof(BITMAPINFOHEADER) + pbih->biClrUsed * sizeof(RGBQUAD);
	memcpy(bufP, lpBits, (int)(pbih->biSizeImage));
	delete lpBits;

	result.buffer = buf;
	result.size = bufSize;

	return result;
}
