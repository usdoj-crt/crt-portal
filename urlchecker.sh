#!/bin/bash
# link testing
# source urlchecker.sh /Users/katiewitham/crt-portal
main_directory=$1
# need to figure out way to exclude more directories
excluded_directory="*/node_modules/*"
all_urls=()
all_files=()
# add new headers file to get curl responses
touch headers
# clear output file
echo -n "" > output.csv
# find links in all files in main directory except excluded directory 
sudo find $main_directory -type f ! -path $excluded_directory -exec grep -iREo "(http|https)://[a-zA-Z0-9./?=_%:-]*" {} \; | while read url;
# separate links from files and trim links
do
   all_files+=(${url})
   plain_url=${url#*:}
   trimmed_url=$(echo "$plain_url" | sed 's:/*$::' | sed 's/\.$//')
   all_urls+=(${trimmed_url})
done
# check response for all unique urls
unique_urls=($(tr ' ' '\n' <<<"${all_urls[@]}" | awk '!u[$0]++' | tr '\n' ' '))
for i in "${unique_urls[@]}"
do
    curl ${i} -I -o headers -s
    response=$(cat headers | head -n 1 | cut '-d ' '-f2')
    in_files=()
    if [ -n $response ]
    then
        if [ $response -eq 404 ]
        then
        # if we get a 404 find matching index for file so we can put the url and the file where it was found in the csv
            for (( j=0; j<=${#all_urls[@]}; j++ )); do
                if [ ${all_urls[$j]} = ${i} ]
                then
                    in_files+=("${all_files[$j]}")
                fi
            done
            echo "$i - $in_files" >> output.csv

        fi
    fi
done
# remove headers file as it's no longer needed
if [ -f "headers" ] ; then
    rm "headers"
fi