import redis
from dotenv import load_dotenv
load_dotenv()

redis_session = redis.Redis(host='redis', port=6379, decode_responses=True,db=0 )
redis_tfcache = redis.Redis(host='redis', port=6379, decode_responses=True,db=1 )

# redis = redis.Redis(
#     host=os.environ.get("REDIS_HOST"),
#     port=12326,
#     decode_responses=True,
#     username="default",
#     password=os.environ.get("REDIS_PASSWORD"),
# )


