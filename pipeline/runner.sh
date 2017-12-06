export PATH="$(pwd):$PATH"
for file in $1.txt; do
  $file;
done;
