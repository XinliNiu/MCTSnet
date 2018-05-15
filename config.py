OPTIM = "SGD"
MOMENTUM = .9

BATCH_SIZE=32

NUM_SIMS = 12

MIN_MEMORIES = BATCH_SIZE*3
MAX_MEMORIES = 30000

NUM_EPISODES=10

SCORING_THRESHOLD = 1.39 #if wins by at least 2

NUM_TOURNAMENT_EPISODES=5

ALPHA=.8
EPSILON=.2
TAU = 1
TURNS_UNTIL_TAU0 = 10

LR = .1

WEIGHT_DECAY = 0.00001


TRAINING_LOOPS=10
NUM_BATCHES_PER_TRAINING=TRAINING_LOOPS

CH = 3
R = 6
C = 7

###
STATE_SHAPE = (CH, R, C)

NUM_CHOICES = STATE_SHAPE[1] * STATE_SHAPE[2]

BATCHED_SHAPE = (BATCH_SIZE, STATE_SHAPE[0]+1, STATE_SHAPE[1], STATE_SHAPE[2])