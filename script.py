import os
from os import remove
from os import path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# from wordcloud import WordCloud, STOPWORDS
import re
from time import sleep
import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
import json
import csv

from bs4 import BeautifulSoup
from linkedin_scraper import actions
# import asyncio
def logins(browser):
    url = "https://www.linkedin.com/login/es?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
    browser.get(url)
    
    # email = os.getenv('')
    # password = os.getenv('')
    actions.login(browser, email, password)
    
    
def scrollPages (numpost, browser, typeP):
    # el scroll de las reacciones en los post
    profileScroll = browser.find_elements(By.XPATH, '//div[@class="social-details-social-activity update-v2-social-activity"]')
    lenProfilePage = len(profileScroll)
    # scrollsPage = 0

    while numpost >= lenProfilePage:         
#         scroll dow
        try:
            btnScrollPage= browser.find_element(By.XPATH, './/button[@class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')
            btnScrollPage.click()
            sleep(random.uniform(3.0,5.0))
            
            btnScrollPage= browser.find_element(By.XPATH, '//button[@class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')
            profileScroll = browser.find_elements(By.XPATH, '//div[@class="social-details-social-activity update-v2-social-activity"]')
            lenProfilePage = len(profileScroll)
        except:
            print(f'X compania solo ha publicado {lenProfilePage} post de {typeP}, y estamos buscando {numpost} post.')
#         scroll up
            browser.execute_script("window.scrollTo(0, +600);")
            break
#     regresa al inicio de la página para iniciar el scraping en cada post
    browser.execute_script("window.scrollTo(0, +600);")
        

def lookLikes (numpost, browser, typeP, date):
    # pantallan de inicio
    total_post = browser.find_elements(By.XPATH, '//div[@class="social-details-social-activity update-v2-social-activity"]')
    longpost = len(total_post)
    
# ---------------------------------------------------------------------------------------    
    src = browser.page_source
    soup = BeautifulSoup(src, features="lxml")
    
    comments = []
    comments_bs4tags = soup.find_all("button", attrs = {"class" : re.compile("t-black--light social-details-social-counts__count-value.*")})
    for tag in comments_bs4tags:
        strtag = str(tag)
        list_of_matches = re.findall('[,0-9]+',strtag)
        last_string = list_of_matches.pop()
        int_comment = int(last_string)
        comments.append(int_comment)
    print(f'comments: {comments}')
    
    shares = []
    share_bs4tags = soup.find_all("button", attrs = {"class" : re.compile("ember-view t-black--light.*")})
    for tag in share_bs4tags:
        strtag = str(tag)
        list_of_matches = re.findall('[,0-9]+',strtag)
        last_string = list_of_matches.pop()
        int_share = int(last_string)
        shares.append(int_share)

    print(f'shares: {shares}')

# ---------------------------------------------------------------------------------------    

    # Scrape the data of 1 Linkedin profile, and write the data to a .CSV file
    with open(typeP + '-linkedin-' + str(numpost) + '-date-'+ str(date) + '-posts.csv', 'w',  newline = '', encoding="utf-8") as file_output:
        headers = ['idPost','typePost', 'date', 'like', 'comment', 'share', 'vectorName', 'vectorJob', 'vectorLinkedin']
        writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n',fieldnames=headers)
        writer.writeheader()  
    
        contPost =0
        count_comment = 0
        count_share = 0
        DataProfile = [] # vector para almacenar en archivo JSON.
        
        vector_comment = [] # vector para almacenar en archivo JSON.
        vector_share = []    # vector para almacenar en archivo JSON.
        for post in total_post:
            
            contPost+=1
            idPost = contPost
            typePost = typeP
            ventorlikes = []# para almacenar en archivo JSON.
            
            vector_comment = [] # para almacenar en archivo JSON.
            vector_share = []    # para almacenar en archivo JSON.
            if numpost >= contPost:
                try:
                    stringLike = post.find_element(By.XPATH, './/span[@class="social-details-social-counts__reactions-count"]')
                    like = int(stringLike.text)
                    ventorlikes.append(like) # para almacenar en archivo JSON.
                except:
                    stringLike = post.find_element(By.XPATH, './/span[@class="social-details-social-counts__social-proof-fallback-number"]')
                    like = int(stringLike.text) 
                    ventorlikes.append(like)
                    
#             Se utiliza BeautifulSoup para estraer una list de los valores para posteriormente unirlo al DAtaFrema
                # sleep(2)

                comment = post.find_elements(By.XPATH, './/button[contains(@class, "t-black--light social-details-social-counts__count-value")]')
                if comment == []:
                        comment = 0
                        comment = comment
                else:
                        count_comment +=1
                        len_comments = len(comments)
                        item = (count_comment + (len_comments -1)) - len_comments
                        comment = comments[item]
                vector_comment.append(comment) # para almacenar en archivo JSON.
                

                share = post.find_elements(By.XPATH, './/button[contains(@class, "ember-view t-black--light")]')
                if share == []:
                        share = 0
                        share = share
                else:                    
                        count_share +=1
                        len_share = len(shares)
                        item2 = (count_share + (len_share -1)) - len_share
                        share = shares[item2]
                vector_share.append(share) # para almacenar en archivo JSON.
                        
                print('id {} para Like {}, Comment = {} y Share = {}'.format(contPost, like, comment, share))


# entra en cada reacción del post en la pantalla principal
                sleep(5)
                try:
                    click_likes_one = post.find_element(By.XPATH, ".//span[@class='social-details-social-counts__reactions-count']")
                    click_likes_one.click()
                except:
                    try:
                        click_likes_two = post.find_element(By.XPATH, ".//span[@class='social-details-social-counts__social-proof-text']")
                        click_likes_two.click() 
                    except:
                        continue 
                                   
                sleep(8)
                profile = post.find_elements(By.XPATH, '//div[@class="inline-flex full-width"]')
                lenProfile = len(profile)
                longProfile = lenProfile//5
                scrolls = 0
                while scrolls < longProfile:  
                    try:
                        buttonScroll= browser.find_element(By.XPATH, '//button[@class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')
                        for i in range(longProfile):
                            try:  
                                buttonScroll.click()
                                sleep(random.uniform(3.0,5.0))
                                buttonScroll= browser.find_element(By.XPATH, '//button[@class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')
                            except:
                                break
                        profile = browser.find_elements(By.XPATH, '//div[@class="inline-flex full-width"]')
                        lenProfile = len(profile)
                        longProfile = lenProfile//5
                        scrolls+=1
                    except:
                        break
                sleep(2)


                ProofName_Job = []
                vectorName = []
                vectorJob = []
                vectorLinkedin = []
                j = 0
                for people in profile:  
                    j+=1
                    try:
                        name = people.find_element(By.XPATH, './/span[@dir="ltr"]').text
                        vectorName.append(name)
                        job = people.find_element(By. XPATH, './/div[@class="artdeco-entity-lockup__caption ember-view"]').text
                        vectorJob.append(job)
                        linkedin = people.find_element(By. XPATH, './/a[@class="link-without-hover-state ember-view"]').get_attribute('href')
                        vectorLinkedin.append(linkedin)
                    except:
                        try:
                            name = people.find_element(By.XPATH, './/div[@class="artdeco-entity-lockup__title ember-view"]').text
                            vectorName.append(name)
                            job = ('Cuenta corporativa ' + name) 
                            vectorJob.append(job)
                            linkedin = people.find_element(By. XPATH, './/a[@class="link-without-hover-state ember-view"]').get_attribute('href')
                            vectorLinkedin.append(linkedin)
                            print(f'Se encontró un cuanta corporativa de: {name}  en la posiscion {j-1}')
                        except:
                            name= np.nan
                            vectorName.append(name)
                            job = np.nan
                            vectorJob.append(job)
                            linkedin = np.nan
                            vectorLinkedin.append(linkedin)
                        
                    # sleep(3)
                    try:
                        profileDict = {
                            'name': people.find_element(By.XPATH, './/span[@dir="ltr"]').text,
                            'job' : people.find_element(By. XPATH, './/div[@class="artdeco-entity-lockup__caption ember-view"]').text,

                            'linkedin' : people.find_element(By. XPATH, './/a[@class="link-without-hover-state ember-view"]').get_attribute('href')  
                                                          
                        } 
                    except:
                        try:
                            name = people.find_element(By.XPATH, './/div[@class="artdeco-entity-lockup__title ember-view"]').text
                            profileDict = {
                                'name' : name,
                                'job' : ('Cuenta corporativa '+ name),
                                'linkedin' : people.find_element(By. XPATH, './/a[@class="link-without-hover-state ember-view"]').get_attribute('href')                                  
                            }
                        except:
                                
                            profileDict = {
                                'name' : 'nan',
                                'job' : 'nan',
                                'linkedin' : 'nan'                                 
                            }
                        
                    ProofName_Job.append(profileDict)
                
                writer.writerow({headers[0]:idPost, 
                                headers[1]:typePost, 
                                headers[2]:date,
                                headers[3]:like,
                                headers[4]:comment,
                                headers[5]:share,                                
                                headers[6]:vectorName,
                                headers[7]:vectorJob,
                                headers[8]:vectorLinkedin
                                })
                # sleep(2)
                exit = browser.find_element(By.CLASS_NAME, "mercado-match")
                exit.click()

            else:
                print('\nSe finalizó la cantidad de datos buscados en la APP sobre '+ typeP+'\n')
                break
                
#             code para agregar datos al  archivo JSON
            proof = {          
                    'ID' : contPost,
                    'Date' : date,
                    'TypePost' : typeP,
                    'Likes': like,
                    'comment': comment,
                    'share': share,
                    'Profile': ProofName_Job   
                    }
    
            DataProfile.append(proof)
            
        with open(typeP + '-linkedin-' + str(numpost) + '-date-'+ str(date) + '-posts.json', 'w') as df:
                    json.dump(DataProfile, df, indent = 4)
                
#-------------------------------------------------------------------------------
#                 proceso de filtrar los data recabados de typeP
#-------------------------------------------------------------------------------
    
# Inicializar las variables globales como vacias para utilizarlas en 'def Excel_Write():'
Filter_videos_linkedin = ''
Filter_documents_linkedin = ''
Filter_articles_linkedin = ''
Filter_images_linkedin = ''
dataReaction = '' 
vector_filter = []

dataReaction_videos = '' 
dataReaction_documents = '' 
dataReaction_articles = '' 
dataReaction_images = ''
    
def filter_dataset(df,typeP):

    # filtrar los Likes, Comments y Shares
    dataset = df.iloc[:,[3,4,5]]

    # Agrupar el dataset con: name, job y linkedin 
    listname = []
    for i in range(len(df)):
        l=df.vectorName[i]
        l2=l.replace("[","")
        l2=l2.replace("]","")
        # l2=l2.replace("'","")
        l2 =l2.strip("'")
        x = l2.split("', ")
        listname+=x
    for i in range(len(listname)):
        listname[i] = listname[i].replace("'","")


    listjob = []
    for j in range(len(df)):
        k=df.vectorJob[j]
        G2=k.replace("[","")
        G2=G2.replace("]","")
        # l2=l2.replace("'","")
        G2 =G2.strip("'")
        y = G2.split("', ")
        listjob+=y
    for j in range(len(listjob)):
        listjob[j] = listjob[j].replace("'","")


    list_linkedin = []
    for z in range(len(df)):
        t=df.vectorLinkedin[z]
        f2= t.replace("[","")
        f2=f2.replace("]","")
        # f2=f2.replace("'","")
        # f2 =f2.strip("'")
        w = f2.split("', ")
        list_linkedin += w
    for z in range(len(list_linkedin)):
        list_linkedin[z] = list_linkedin[z].replace("'","")


    lista = pd.Series(listname)
    resultados = lista.value_counts().rename_axis('Name').reset_index(name='Counts likes')

    arrayjob = []
    for item in resultados['Name']:
        index_job= listname.index(item)
        arrayjob.append(listjob[index_job])  

    arraylinkedin = []
    for item in resultados['Name']:
        index_linkedin= listname.index(item)
        arraylinkedin.append(list_linkedin[index_linkedin])

    # agregar columnas al Data Frame de resultados
    resultados["Job"] = arrayjob
    resultados["Linkedin"] = arraylinkedin

    # variables globales para generar archivo Excel
  

#-----------------------------------------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
#-----------------------------------------------------------------------------------------------------------

date = datetime.datetime.today().strftime('%d-%m-%Y')
                                            
#     inicializa el navegado
s = Service(executable_path='./chromedriver.exe')
browser = webdriver.Chrome(service=s)

#     inicia sesión en la página de Linkedin
logins(browser)

# zoom standar para la app
browser.execute_script("document.body.style.zoom='100%'")

# Mantiene el Linkedin en ejecucion después de hacer un Scraping a una publicación
si = 's'
while si == "s" or si == "S":   
    
    #     pregunta por que tipo de publicación quiere investigar
    print (f'Elija que tipo de publicación quiere analizar: \n Imagenes => A \n Videos => B\nArtículos => C \n Documentos => D \n Todos => E')
    PublicationType = str(input()).upper()
    for i in range(1):
            if PublicationType == "A":
                typeP = "images"
            elif PublicationType == "B":
                typeP = "videos"
            elif PublicationType == "C":
                typeP = "articles"
            elif PublicationType == "D":
                typeP = "documents"   
            elif PublicationType == "E":
                typeP = "all"
            else:
                print("Debes escribir un dato valido.")

    #     Pregunta por la  cantidad de posts que se analizán
    print("¿Cuántos post quiere analizar en " + typeP+'?')
    numpost = int(input())
    while numpost <= 0:
        print('Vuelva a ingresar un número mayor que cero.')
        numpost = int(input())


    #     Redirige a la publicación seleccionada
    link = "https://www.linkedin.com/company/.../posts/?feedView="+ typeP +"&viewAsMember=true"
    browser.get(link)

    #     se carga los posts que se solicitan
    sleep(5)
    scrollPages (numpost, browser, typeP)

    #     busca en cada contenido de los posts
    sleep(3)
    lookLikes (numpost, browser, typeP, date)
                                        
    #-------------------------------------------------------------------------------
    # proceso de filtrar los data recabados de typeP
    #-------------------------------------------------------------------------------
                       
    si = input(f'¿Quiere buscar en otra publicación de Linkedin?: \n(Sí => S o s)\n(No => N o n)')
          
#----------------------------------------------------------------------------
#            Generar archivo Excel con las publicaciones analizadas
#----------------------------------------------------------------------------#

sleep(2)          



# eliminar ficheros de dataReaction y Filter del bucle anterios            

              
          
# close browser
browser.quit()
