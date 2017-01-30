from boto import connect_s3
from boto.s3.key import Key
from multiprocessing.pool import ThreadPool

old_bucket_name = "beiwe2"
connection_old = connect_s3(aws_access_key_id="fill_me_in",
                  aws_secret_access_key="fill_me_in")
old_bucket = connection_old.get_bucket(old_bucket_name)

new_bucket_name = "beiwe"
connection_new = connect_s3(aws_access_key_id="fill_me_in",
                  aws_secret_access_key="fill_me_in")
new_bucket = connection_new.get_bucket(new_bucket_name)

# old_mongobackup_bucket_name = "beiwe2-mongo-backups"
# connection_old_mongobackup = connect_s3(aws_access_key_id="AKIAIR7T5SGDINHM2NYA",
#                               aws_secret_access_key="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")
# old_backup_bucket = connection_old_mongobackup.get_bucket(old_mongobackup_bucket_name)

# new_mongobackup_bucket_name = "beiwe-mongo-backup"`e
# connection_new_mongobackup = connect_s3(aws_access_key_id="AKIAIHSAPJHT65RNDS6A",
#                               aws_secret_access_key="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")
# new_backup_bucket = connection_new_mongobackup.get_bucket(new_mongobackup_bucket_name)

def batch_download_upload(file_path_on_old_s3_bucket):
    print file_path_on_old_s3_bucket
    data = Key(old_bucket, file_path_on_old_s3_bucket).read()
    new_bucket.new_key(file_path_on_old_s3_bucket).set_contents_from_string(data)

just_in_time_list_o_files = old_bucket.list(prefix="")
pool = ThreadPool(20)

pool.map(batch_download_upload, just_in_time_list_o_files)
pool.close()
pool.terminate()