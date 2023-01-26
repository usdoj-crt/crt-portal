#!/bin/bash
# This script tests all urls in codebase (excluding the node_module directory) to catch any 404s
# run ./urlchecker.sh in the terminal
main_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
excluded_directory="*/node_modules/*"
all_urls=()
# add new headers file to get curl responses
tmp_header_file=$(mktemp headers)
# clear output file
echo -n "" > output.csv
# find links in all files in main directory except excluded directory 
while read url;
# separate links from files and trim links
do
   plain_url=${url#*:}
   trimmed_url=$(echo "$plain_url" | sed 's:/*$::' | sed 's/\.$//')
   all_urls+=("$trimmed_url")
done < <(find "$main_dir" -type f ! -path "$excluded_directory" -exec grep -iREo "(http|https)://[a-zA-Z0-9./?=_%:-]*" {} \;)
# check response for all unique urls
unique_urls=($(tr ' ' '\n' <<<"${all_urls[@]}" | awk '!u[$0]++' | tr '\n' ' '))
excluded_urls=("$(cat "$main_dir"/excluded_urls)")
for i in ${unique_urls[@]}
do
 # skip urls in excluded_urls file
 if echo ${excluded_urls[@]} | grep -q -w "$i";
   then
        continue
 else
    curl "$i" -I -o headers -s
    response=$(cat headers | head -n 1 | cut '-d ' '-f2')
    in_files=()
  if [ -z "$response" ];
    then
         continue    
  fi
  if [ "$response" -eq 404 ];
     then
     echo "$i" >> output.csv
    # if we get a 404 find matching index for file so we can put the url and the file where it was found in the csv
     files=$(find "$main_dir" -type f -exec grep -rl "$i" {} \;)
     echo "$files" >> output.csv
   
  fi
 fi
done
file_dir=$(echo "$main_dir/output.csv")
sed -i '' "/output.csv/d" $file_dir
# remove headers file as it's no longer needed
rm $tmp_header_file