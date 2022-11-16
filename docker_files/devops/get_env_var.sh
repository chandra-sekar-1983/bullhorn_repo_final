#!/bin/bash
vars=$(cat ./devops/terraform/vars/$1.tfvars)
while IFS= read -r line; do
  line=$(echo $line | tr -d "[:space:]")
  if [[ $line =~ $2 ]] ; then
    match=$(echo $line | sed "s/$2=//g")
    break
  fi
done <<< "$vars"
echo $match | sed "s/\"//g"
