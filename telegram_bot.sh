# Simple Telegram bot written in Bash
#
# Create a bot with https://t.me/botfather, then run this script with the token and you can start interacting with it.
# see https://core.telegram.org/bots/api
#
# Author: Eli Finkel - eyfinkel@gmail.com

set -eu

API_SERVER="https://api.telegram.org"
TOKEN=""
VERBOSE=0


# info message
function inf() {
    local msg=$1
    echo [INFO] `caller | cut -d" " -f1`: $msg >&2
}


# debug message, if VERBOSE is set
function dbg() {
    local msg=$1
    if [ "$VERBOSE" == "1" ]; then
        echo [DEBUG] `caller | cut -d" " -f1`: $msg >&2
    fi
}


# error message and exit
function err() {
    local msg=$1
    echo [ERROR] `caller | cut -d" " -f1`: $msg >&2
    exit 1
}


# pass json object and filter and get result
function json_field() {
    local json="$1"
    local filter="$2"
    
    echo "$json" | jq -er "$filter"
}


# escape text to be used as part of uri
function uri_escape() {
    local arg="$1"
    
    echo "$arg" | jq -eRr @uri
}


# parse options
function parse_opts() {
    while getopts ":vht:" opt; do
        case $opt in
            v)
                VERBOSE=1
                dbg "VERBOSE set"
                ;;
            h)
                err "Usage: $0 -t <token> -v"
                ;;
            t)
                TOKEN="$OPTARG"
                dbg "TOKEN set"
                ;;
            *)
                err "Unknown parameter: $OPTARG. Use '-h' for usage"
                ;;
        esac
    done
    
    if [ -z "$TOKEN" ]; then err "Missing bot token. Use '-h' for usage"; fi
}


# call an api
function call_api() {
    local method="$1"
    local name="$2"
    
    dbg "Calling API: '$method:$name'"
    ret=`curl -fsS --request "$method" "$API_SERVER/bot$TOKEN/$name"` || err "API error"
    dbg $ret
    echo $ret
}


# main loop: poll and handle updates
function update_loop() {
    local update_offset=0
    while true; do
        local update=`call_api GET "getUpdates?offset=$update_offset&limit=1&timeout=5"`
        local update_length=`json_field "$update" ".result | length"`
        if [ $update_length -eq 0 ]; then continue; fi
        
        local update_offset=`json_field "$update" .result[0].update_id`
        local message=`json_field "$update" .result[0].message`
        local id=`json_field "$message" .from.id`
        local username=`json_field "$message" .from.username`
        local text=`json_field "$message" .text`
        ((update_offset++))
        
        inf "Received message from $username: $text"
        
        case "$text" in
            "/start")
                local reply=`uri_escape "Hi there $username, let's start"`
                call_api GET "sendMessage?chat_id=$id&text=$reply" >/dev/null
                ;;
            "bye")
                local reply=`uri_escape "Bye $username"`
                call_api GET "sendMessage?chat_id=$id&text=$reply" >/dev/null
                ;;
            *)
                local reply=`uri_escape "Not sure what to do with '$text'"`
                call_api GET "sendMessage?chat_id=$id&text=$reply" >/dev/null
                ;;
        esac
    done
}


# parse opts and start
parse_opts $@
me=`call_api GET getMe`
inf "Running - Bot `json_field "$me" .result.username` (ID `json_field "$me" .result.id`)"
update_loop
