import speech_recognition as sr
import pyttsx3
import nltk
import pandas as pd
import random
import time

# Download the 'punkt' package if it's not already downloaded
nltk.download('punkt')

# Initialize the recognizer and the text-to-speech engine
r = sr.Recognizer()
engine = pyttsx3.init()

# Take student's name and RBTNo as input
student_name = input("Please enter your name: ")
RBTNo = input("Please enter your RBTNo: ")

# List of questions, answers, and hints
qa_pairs = [
    {"question":"\nData integrity constraints are used to\n•	A. Control who is allowed access to the data\n•	B. Ensure that duplicate records are not entered into the table\n•	C. Improve the quality of data entered for a specific property\n•	D. Prevent users from changing the values stored in the table","answers":"Improve the quality of data entered for a specific property","hint":"Ensures accuracy and consistency of data"},
    {"question":"Establishing limits on allowable property values, and specifying a set of acceptable, predefined options that can be assigned to a property are examples of:\n•	A. Attributes\n•	B. Data integrity constraints\n•	C. Method constraints\n•	D. Referential integrity constraints","answers":"Data integrity constraints","hint":"Rules or types for data."},
    {"question":"Domain constraints, functional dependency and referential integrity are special forms of _.\n•	A. Foreign key\n•	B. Primary key\n•	C. Assertion\n•	D. Referential constraint","answers":"Assertion","hint":"Conditions for a database."},
    {"question":"Foreign key is the one in which the _ of one relation is referenced in another relation.\n•	A. Foreign key\n•	B. Primary key\n•	C. References\n•	D. Check constraint","answers":"Primary key","hint":"Field pointing to another table."},
    {"question":"The descriptive property possessed by each entity set is _\na) Entity\nb) Attribute\nc) Relation\nd) Model","answers":"Attribute","hint":"Characteristics of an entity."},
    {"question":"What term is used to refer to a specific record in your music database; for instance; information stored about a specific album?\na) Relation\nb) Instance\nc) Table\nd) Column","answers":"Instance","hint":"Individual occurrence of an entity."},
    {"question":"Which of the following gives a logical structure of the database graphically?\na) Entity-relationship diagram\nb) Entity diagram\nc) Database diagram\nd) Architectural representation","answers":"Entity relationship diagram","hint":"Diagram for entities and relationships."},
    {"question":"Which of the following is used to call the procedure given below ?\nCreate procedure dept_count proc(in dept name varchar(20),\nout d count integer)\nbegin\nselect count(*) into d count\nfrom instructor\nwhere instructor.dept name= dept count proc.dept name\nend\na)Declare d_count integer;\nb) Declare d_count integer;\ncall dept_count proc(’Physics’, d_count);\nc)Declare d_count integer;\n   call dept_count proc(’Physics’);\nd)Declare d_count; \n   call dept_count proc(’Physics’, d_count);","answers":"option b","hint":"Procedure call syntax."},
    {"question":"A _ is a special kind of a store procedure that executes in response to certain action on the table like insertion, deletion or updation of data.\na) Procedures\nb) Triggers\nc) Functions\nd) None of the mentioned","answers":"Triggers","hint":"Procedure that triggers on an event."},
    {"question":"Triggers are supported in\na) Delete\nb) Update\nc) Views\nd) All of the mentioned","answers":"Update","hint":"Operations causing a trigger."},
    ]

# Select 5 random questions
selected_questions = random.sample(qa_pairs, 5)

# Initialize DataFrame to store quiz results
quiz_results = pd.DataFrame(columns=["Student Name", "RBTNo", "Question", "User Answer", "Correct Answer"])

# Function to ask a question and get an answer
def ask_question(question, hint):
    print(question)
    # Convert the question to speech
    engine.say(question)
    engine.runAndWait()

    attempts = 0
    hint_used = False
    while attempts <= 3:  # Limit the number of attempts to 3
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            answer = r.recognize_google(audio)
            print("Your answer: {}\n".format(answer))
            return answer, hint_used
        except sr.UnknownValueError:
            attempts += 1
            print("Google Speech Recognition could not understand audio.")
            use_hint = input("Would you like to use a hint? (yes/no): ")
            if use_hint.lower() == "yes":
                print("Hint: {}".format(hint))  # Provide a hint if the user wants it
                hint_used = True
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return None, hint_used

# Initialize score
score = 0

# Start the timer
start_time = time.time()

# Ask each question
for qa_pair in selected_questions:
    user_answer, hint_used = ask_question(qa_pair["question"], qa_pair["hint"])
    # If the user's answer is incorrect, ask if they want a hint
    if user_answer.lower() != qa_pair["answers"].lower():
        use_hint = input("Your answer is incorrect. Would you like to use a hint? (yes/no): ")
        if use_hint.lower() == "yes":
            print("Hint: {}".format(qa_pair["hint"]))  # Provide a hint if the user wants it
            hint_used = True
            user_answer, _ = ask_question(qa_pair["question"], qa_pair["hint"])  # Ask the question again
        else:
            print("Let's try again.")
            user_answer, _ = ask_question(qa_pair["question"], qa_pair["hint"])  # Ask the question again
    # Grade the answer
    # Convert the answers to sets of words
    answer_words = set(nltk.word_tokenize(user_answer.lower()))
    correct_answer_words = set(nltk.word_tokenize(qa_pair["answers"].lower()))
    # Calculate the Jaccard similarity
    jaccard_similarity = len(answer_words.intersection(correct_answer_words)) / len(answer_words.union(correct_answer_words))
    # If the Jaccard similarity is above a certain threshold, consider the answer correct
    if jaccard_similarity > 0.5:
        score += 2
        if hint_used:  
            # If a hint was used, reduce the score by 0.5
            score -= 0.5
    else:
        # If the answer is incorrect, decrease the score
        score -= 0
    # Store the question, user's answer, and correct answer in the DataFrame
    quiz_results = pd.concat([quiz_results, pd.DataFrame([{"Student Name": student_name, "RBTNo": RBTNo, "Question": qa_pair["question"], "User Answer": user_answer, "Correct Answer": qa_pair["answers"]}])], ignore_index=True)

# End the timer
end_time = time.time()

# Calculate the duration of the quiz
quiz_duration = end_time - start_time

print("Your score is: {}/{}".format(score, len(qa_pairs)))
print("Time taken: {:.2f} seconds\n".format(quiz_duration))

# Create a DataFrame for the final score
final_score_df = pd.DataFrame([{"RBTNo": RBTNo, "Final Score": score}])

# Add the final score and quiz duration to the DataFrame
quiz_results.loc[len(quiz_results)] = [student_name, RBTNo, "Final Score", score, ""]
quiz_results.loc[len(quiz_results)] = [student_name, RBTNo, "Quiz Duration", "{:.2f} seconds".format(quiz_duration), ""]

# Write the final score to a separate CSV file
with open('final_scores.csv', 'a') as f:
    final_score_df.to_csv(f, header=f.tell()==0, index=False)
