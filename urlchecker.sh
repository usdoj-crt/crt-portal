#!/bin/bash
# url testing
# source urlchecker.sh
main_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
excluded_directory="*/node_modules/*"
all_urls=()
all_files=()
match_file()
{
  for (( j=0; j<=${#all_urls[@]}; j++ )); do
    if [ ${all_urls[$j]} = ${1} ]
      then
        in_files+=("${all_files[$j]}")
       fi
    done
    echo "$in_files" >> output.csv
}
# add new headers file to get curl responses
tmpheaderfile=$(mktemp headers)
# clear output file
echo -n "" > output.csv
# find links in all files in main directory except excluded directory 
sudo find $main_dir -type f ! -path $excluded_directory -exec grep -iREo "(http|https)://[a-zA-Z0-9./?=_%:-]*" {} \; | while read url;
# separate links from files and trim links
do
   all_files+=(${url})
   plain_url=${url#*:}
   trimmed_url=$(echo "$plain_url" | sed 's:/*$::' | sed 's/\.$//')
   all_urls+=(${trimmed_url})
done
# check response for all unique urls
unique_urls=($(tr ' ' '\n' <<<"${all_urls[@]}" | awk '!u[$0]++' | tr '\n' ' '))
excluded_urls=("`cat $main_dir/excluded_urls`")
for i in "${unique_urls[@]}"
do
 # skip urls in excluded_urls file
 if echo ${excluded_urls[@]} | grep -q -w "${i}";
   then
        continue
 else
    curl ${i} -I -o headers -s
    response=$(cat headers | head -n 1 | cut '-d ' '-f2')
    in_files=()
  if [ -z ${response} ];
    then
         continue
      
  fi
  if [ ${response} -eq 404 ];
     then
    # if we get a 404 find matching index for file so we can put the url and the file where it was found in the csv
    match_file $i
  fi
 fi
done
# remove headers file as it's no longer needed
rm ${tmpheaderfile}