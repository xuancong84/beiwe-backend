# there is also $2, which is the study object id
export PATH="$(pwd):$PATH"
for file in $(cat $1.txt); do
  Beiwe-Analysis/$file;
done;
