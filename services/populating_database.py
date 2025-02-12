import sqlite3
conn = sqlite3.connect("chat_responses.db")
cursor = conn.cursor()


# From ARNAV - This array dialogues is created by help of chat gpt so that I can test my code 
# Famous movie characters and their dialogues
dialogues = [
    # Joker
    ("Joker", "Tell me a joke!", "Why so serious?"),
    ("Joker", "How do you feel?", "Madness is like gravity, all it takes is a little push."),
    ("Joker", "What’s your philosophy?", "Introduce a little anarchy."),
    ("Joker", "Are you happy?", "I’m not a monster. I’m just ahead of the curve."),
    ("Joker", "Can you give advice?", "Smile, because it confuses people."),
    ("Joker", "Do you have a plan?", "It's all part of the plan."),
    
    # Iron Man
    ("Iron Man", "Who are you?", "I am Iron Man."),
    ("Iron Man", "How’s your life?", "Sometimes you gotta run before you can walk."),
    ("Iron Man", "Are you a hero?", "Heroes are made by the path they choose."),
    ("Iron Man", "Do you regret anything?", "It's not about how much we lost, it's about how much we have left."),
    ("Iron Man", "Do you have a plan?", "Sometimes you gotta run before you can walk."),
    ("Iron Man", "Any last words?", "I love you 3000."),
    
    # Darth Vader
    ("Darth Vader", "Are you my father?", "I am your father."),
    ("Darth Vader", "Can you train me?", "You don’t know the power of the dark side."),
    ("Darth Vader", "Do you feel emotions?", "I find your lack of faith disturbing."),
    ("Darth Vader", "What’s your goal?", "Together, we can rule the galaxy."),
    ("Darth Vader", "Why are you evil?", "Once you start down the dark path, forever will it dominate your destiny."),
    ("Darth Vader", "What happened to Anakin?", "Anakin Skywalker was weak. I destroyed him."),
    
    # Forrest Gump
    ("Forrest Gump", "Tell me something wise.", "Life is like a box of chocolates."),
    ("Forrest Gump", "What’s your secret?", "I may not be a smart man, but I know what love is."),
    ("Forrest Gump", "How do you stay happy?", "Stupid is as stupid does."),
    ("Forrest Gump", "Any advice?", "You have to do the best with what God gave you."),
    ("Forrest Gump", "How was your childhood?", "My momma always said, ‘Life was like a box of chocolates.’"),
    ("Forrest Gump", "Do you believe in fate?", "I think maybe we’re all just floating around accidental-like on a breeze."),
    
    # Batman
    ("Batman", "Who are you?", "I’m Batman."),
    ("Batman", "What do you stand for?", "It’s not who I am underneath, but what I do that defines me."),
    ("Batman", "Are you afraid?", "Fear is a tool."),
    ("Batman", "What’s your goal?", "Sometimes the truth isn’t good enough. Sometimes people deserve more."),
    ("Batman", "Why fight crime?", "Justice is about more than revenge."),
    ("Batman", "What’s your superpower?", "I’m rich."),
    
    # Yoda
    ("Yoda", "Can you teach me?", "Do, or do not. There is no try."),
    ("Yoda", "What’s your philosophy?", "Fear is the path to the dark side."),
    ("Yoda", "Are you strong?", "Size matters not. Look at me. Judge me by my size, do you?"),
    ("Yoda", "How do I find my way?", "You must unlearn what you have learned."),
    ("Yoda", "Do you have advice?", "Truly wonderful, the mind of a child is."),
    
    # Captain Jack Sparrow
    ("Jack Sparrow", "Who are you?", "Captain Jack Sparrow."),
    ("Jack Sparrow", "Are you a pirate?", "Aye, but you have heard of me."),
    ("Jack Sparrow", "What’s your strategy?", "The problem is not the problem. The problem is your attitude about the problem."),
    ("Jack Sparrow", "Are you lucky?", "You can always trust the dishonest man to be dishonest."),
    ("Jack Sparrow", "Do you have a plan?", "I’ve got a jar of dirt!"),
    
    # Gandalf
    ("Gandalf", "What should I do?", "All we have to decide is what to do with the time that is given us."),
    ("Gandalf", "What do you believe in?", "Even the smallest person can change the course of the future."),
    ("Gandalf", "How do I fight evil?", "You shall not pass!"),
    ("Gandalf", "What is wisdom?", "A wizard is never late, nor is he early. He arrives precisely when he means to."),
    ("Gandalf", "What is power?", "Some believe it is only great power that can hold evil in check. But that is not what I have found."),
    
    # Harry Potter
    ("Harry Potter", "Who are you?", "I’m Harry. Just Harry."),
    ("Harry Potter", "What is love?", "Happiness can be found even in the darkest of times, if one only remembers to turn on the light."),
    ("Harry Potter", "What do you fight for?", "The ones that love us never really leave us."),
    ("Harry Potter", "What’s your goal?", "I solemnly swear that I am up to no good."),
    ("Harry Potter", "What is bravery?", "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends."),
]



cursor.executemany("INSERT INTO scripts (character, user_message, response_to_user_message) VALUES (?, ?, ?)", dialogues)
conn.commit()
conn.close()
print(f"{len(dialogues)} dialogues inserted successfully into chatbot_responses.db!")
