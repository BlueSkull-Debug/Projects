#create rock paper scissors game using a GUI (adding more function)
import random
import tkinter as tk
window = tk.Tk()
window.configure(bg="light blue")
window.geometry("350x240")
window.resizable(0,0) #if I remove this line, it will allow to max size the game window
window.title("Rock Paper Scissors Game")

USER_SCORE = 0
COMP_SCORE = 0
USER_CHOICE = ""
COMP_CHOICE = ""
def choice_to_number(choice):
    rps = {'rock':0,'paper':1,'scissor':2}
    return rps[choice]
def number_to_choice(number):
    rps={0:'rock',1:'paper',2:'scissor'}
    return rps[number]
def random_computer_choice():
    return random.choice(['rock','paper','scissor'])
def result(human_choice,comp_choice):
    global USER_SCORE
    global COMP_SCORE
    user=choice_to_number(human_choice)
    comp=choice_to_number(comp_choice)
    if(user==comp):
        print("Tie")
    elif((user-comp)%3==1):
        print("You win")
        USER_SCORE+=1
    else:
        print("Comp wins")
        COMP_SCORE+=1
    text_area = tk.Text(master=window,height=15,width=49, bg="#FFFF98")
    text_area.grid(column=0,row=8, pady=20, padx=10) #tells how big text area need to be
    answer = "Your Choice: {uc} \nComputer's Choice : {cc} \n Your Score : {u} \n Computer Score : {c} ".format(uc=USER_CHOICE,cc=COMP_CHOICE,u=USER_SCORE,c=COMP_SCORE)
    text_area.insert(tk.END,answer)

def rock():
    global USER_CHOICE
    global COMP_CHOICE
    USER_CHOICE = 'rock'
    COMP_CHOICE = random_computer_choice()
    result(USER_CHOICE, COMP_CHOICE)

def paper():
    global USER_CHOICE
    global COMP_CHOICE
    USER_CHOICE = 'paper'
    COMP_CHOICE = random_computer_choice()
    result(USER_CHOICE, COMP_CHOICE)

def scissor():
    global USER_CHOICE
    global COMP_CHOICE
    USER_CHOICE = 'scissor'
    COMP_CHOICE = random_computer_choice()
    result(USER_CHOICE, COMP_CHOICE)

button1 = tk.Button(text="       Rock       ", bg="skyblue", command=rock)
button1.grid(column=0, row=1)
button2 = tk.Button(text="       Paper      ", bg="pink", command=paper)
button2.grid(column=0, row=2)
button3 = tk.Button(text="      Scissor     ", bg="lightgreen", command=scissor)
button3.grid(column=0, row=3)
window.mainloop()

