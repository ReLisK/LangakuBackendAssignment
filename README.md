# Mantra Backend Engineer Assignment

## Flashcard Scheduling Algorithm Explanation
I initially built a more straightforward/simple algorithm that set an initial interval for each of the possible 3 ratings:
- Rating 0 (Again) - Interval of 1 minute
- Rating 1 (Hard) - Interval of 3 days
- Rating 2 (Easy) - Interval of 5 days

The application would track how many times a user has seen card (continuos_days) and multiplied that by the initial intervals to get a new Interval.
Selecting **Again*** would reset continous days to 0, i.e interval falls back to 1 minute. This algorithm works but would not provide the best experience as it 
doesnt capture and adapt to how *difficult* a user found a card; especially in the crucial stage when a user is reviewing a card.

I then did some research and learnt about the SM2 algorithm and decided that was a better way to handle this problem as it provides multiple ways of addressing
difficulty. The key one being **Ease**, when this is adjusted up or down it affects the length of an interval when a user selects an Easy rating for a card. 

I adapted this main idea and modified it for our algorithm here to fit our 3 rating system (where SM2 has five) along with some other slight changes.

### There are 4 key terms for this algorithm

1. Rating (shown above).
2. State - There are 3 states: 
   - Learning - This is the state of a brand new card or a card that the user has never given a rating of hard or easy to.
   - Reviewing - This is the state of a card after a user has given it a rating of hard (twice) or easy once.
   - Relearning - This is the state of a card if it was in the reviewing state when a user gives it a rating of 0 - "Again".
3. Step - This provides steps or levels to each state that allow us to control when a card transitions to another state. For e.g we can make a user have to select a hard rating twice, to move a card state to reviewing.
4. Ease - This is a interval multiplier that aims to capture card difficulty. It starts at a default of 2.5 and is adjusted up/down based on the users selected ratings. It is used as a multiple to interval when a user
selects Easy for a card that is in the **reviewing stage**. Nb ease cannot fall below 1.3.

### Example Sequence
Using these terms I can then use some examples to explain how the algorithm works, See what happens in the algorithm for a brand new card with the sequence of ratings below:

1. Again

   - Interval is 1 minute
   - Ease,step,state remain unchanged (still Learning).

2. Hard

   - Step is increased to 1
   - a default interval of 6 minutes is applied.
   - Ease and state are still unchanged.

3. Hard

   - Since Step is now 1 the card state transitions to Reviewing
   - A default interval of 1 day is applied.
   - Ease is still unchanged (remember ease it only changes in reviewing state)

4. Hard

   - User finds this card difficult and as such it should appear sooner.
   - interval = previous_interval * HARDBIAS
              = 1 day * 1.2
              = 1.2days
   - As the card is in the Reviewing state the **Ease is reduced by 0.15** : (2.5 - 0.15) = 2.35

5. Easy

   - User finds this card easy and as such doesnt need to see it as quickly.
   - interval = previous_interval * EASYBIAS * **ease**
              = 1.2day * 1.2 * 2.35
              = ~3.4days
   - As the card is in the Reviewing state the **Ease is increased by 0.15** : (2.35 + 0.15) = 2.5

6. Again

   - The card state is changed to Relearning
   - A default interval of 1 minute is applied.
   - **Ease is also reduced by 0.2** (User failed the card as they find it very difficult..User needs to see this card more frequently)

Two things to note:
- Only Easy moves a card from Relearning back to the Reviewing state.
- If a user select Easy for a brand new card, it immediately goes to Reviewing state and assigns a interval of 3 or 4 days.

## Functional Rules
1. Immediate Retry - This is built in; a rating of 0 always sets the interval to 1 minute.
2. Spacing Logic
   - A rating of 2 on first time seeing a card gives the longest initial interval of 4 days.
   - A rating of 1 always results in a interval somewhere between 0 and 2. This is because a rating of 2 is multiplied by ease, whilst 0 always sets interval to 1.
3. Monotonic Intervals - Subsequent correct answers (1 or 2) can never shorten the interval.

## Initial Setup

- uv is recommended for managing virtual environments.

Install postgressql and create db.

git clone the application to your machine.

Modify settings file by including new db user and password eg:

```
# In production this would clearly be in an environment config file or something and not stored in clear text of course. But just for testing:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "FlashcardScheduler",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5433",
    }
}
```

cd to the application location. e.g. cd ./application_location/general-assignment-template/

run
```
uv sync --all-groups

uv run manage.py makemigrations

uv run manage.py migrate
```

## Testing application

- You can use your preferred API tester, I use an application called postman.
- To view API spec go to http://127.0.0.1:8000/api/schema/swagger-ui/#/

run
```
uv run manage.py runserver

# This initializes test data for you.
Send an api POST call to http://127.0.0.1:8000/init_data/
```
***Note that the init_data POST will return user and card id's to the console that you can use for your testing.***

Go ahead and test!

POST /reviews

GET /users/{id}/due-cards?until=ISO8601

