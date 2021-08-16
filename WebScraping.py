#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 13:12:08 2021

@author: alan
"""

import gender_guesser.detector as gender
from selenium import webdriver
import requests
import time
from webdriver_manager.chrome import ChromeDriverManager
import logging.config
import os
import sys
import unidecode
import six
import pause
import argparse
import logging.config
import re
import time
import random
import json
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from Sender import *


class Scraping:

    def __init__(self, folio, name, edad, words, fileName):
        self.words = words
        self.fileName = fileName
        self.name = name
        self.edad = edad
        self.folio = folio
        self.LOGGER = logging.getLogger()
        self.URL = "https://omedic.com.mx/admin/"
        self.SUBMIT_BUTTON_XPATH = "/html/body/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div[6]/button"
        self.username = 'admin2020'
        self.password = 'OmedicAdmin212121'
        # instalando el web driver de chrome mas reciente e instanciandolo
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options)

    def search(self):
        self.LOGGER.info('Searching by folio number')
        self.LOGGER.info("Entering folio")
        folioInput = self.driver.find_element_by_xpath(
            "//input[@id='folio_bus']")
        folioInput.clear()
        folioInput.send_keys(self.folio)
        self.LOGGER.info("Searching")
        self.driver.find_element_by_xpath("//button[@type='submit']").click()
        self.LOGGER.info("Successfully ")

    def login(self):
        try:
            self.LOGGER.info("Requesting page: " + self.URL)
            self.driver.get(self.URL)
        except TimeoutException:
            self.LOGGER.info("Page load timed out but continuing anyway")

        self.LOGGER.info("Waiting for login fields to become visible")

        self.LOGGER.info("Entering username and password")
        email_input = self.driver.find_element_by_xpath(
            "//input[@name='usuario_admin']")
        email_input.clear()
        email_input.send_keys(self.username)

        password_input = self.driver.find_element_by_xpath(
            "//input[@name='password_admin']")
        password_input.clear()
        password_input.send_keys(self.password)

        self.LOGGER.info("Logging in")
        self.driver.find_element_by_xpath("//button[@type='submit']").click()

        self.LOGGER.info("Successfully logged in")

    def validate(self):
        self.login()
        self.search()
        pxName = self.driver.find_element_by_xpath("//input[@name='nombre']")
        admiName = pxName.get_attribute('value')
        if unidecode.unidecode(admiName).lower().split() != unidecode.unidecode(self.name).lower().split() :
            print('\n \n Nombre del paciente incorrecto, debido a que en admin se tiene {} y en Eli se tiene {}'.format(unidecode.unidecode(admiName).lower(), unidecode.unidecode(self.name).lower()))
            flagN = False
        else:
            flagN = True
        
        cupon = self.driver.find_element_by_xpath("//select[@name='cupon']")
        cuponVal = cupon.get_attribute('value')
        
        pxAge = self.driver.find_element_by_xpath("//input[@name='edad']")

        if pxAge.get_attribute('value') != self.edad:
            print('\n \n Edad del paciente incorrecta, debido a que en admin se tiene {} y en Eli se tiene {} años '.format(pxAge.get_attribute('value'), self.edad))
            flagE = False
        else:
            flagE = True

        rws = self.driver.find_elements_by_xpath("//table/tbody/tr")
        r = len(rws)
            # to get column count of table
        cols = self.driver.find_elements_by_xpath("//table/tbody/tr[1]/td")
        # len method is used to get the size of that list
        c = len(cols)
        elemt = []
        
        if len(cuponVal) == 0:
            lr = r-2
        else:
            lr = r-3
        
        # iterate over the rows
        for i in range(lr):
            row = []
        # iterate over the columns
            for j in range(c):
                # getting text from the ith row and jth column
                d = self.driver.find_element_by_xpath(
                    "//table/tbody/tr["+str(i+1)+"]/td["+str(j+1)+"]").text
                row.append(d)
        # finally store and print the list in console
            elemt.append(row)
        #print (elemt)
        lab = [study[1] for study in elemt if study[2] == 'Laboratorios' and study[1].split(
        )[0] != 'Equipo' and study[1].split()[0] != 'Zona']
        count = 0
        for est in lab:
            est = unidecode.unidecode(est).lower().split()
            try:
                wordsUni = [unidecode.unidecode(w).lower() for w in self.words]
                indices = [i for i, w in enumerate(wordsUni) if w == est[0]]
            except ValueError:
                print(
                    "\n \n No se encontro ningún estudio con la palabra {}".format(est[0]))
            flag = False
            for ix in indices:
                labs = wordsUni[ix: ix + len(est)]
                wordsEqual = sum([e1 == e2 for e1 in labs for e2 in est])
                #print(wordsEqual)
                #print (len(est))
                if len(est) >= 3:
                    if  wordsEqual >=  round(len(est) * .75) :
                        flag = True
                else:
                   # print ( labs, est)
                    if set(labs) == set (est):
                        flag = True
            count += flag
            if flag == False:
                print('\n \n No se encontró el estudio de {}'.format(
                    ' '.join(est)))
                    
        if count == len(lab):
            flagL = True
        else:
            flagL = False
        if flagL and flagE and flagN == True:
            print('\n \n La edad, el nombre y los estudios son correctos')
       # for l in lab:
        #    print (l)
        resp = input(
            " \n ¿Gusta enviar el resultado del folio {}? \n  Si (s) / No (n) : ".format(self.folio))
        if resp.lower() == 's':
            pxcorreo = self.driver.find_element_by_xpath("//input[@name='correo']")
            send(pxcorreo.get_attribute('value'), self.fileName, self.folio, self.name)
        resp = input(
            " \n ¿Gusta subir el resultado del folio {}? \n  Si (s) / No (n) : ".format(self.folio))
        if resp.lower() == 's':
            self.driver.find_element_by_link_text("Subir resultados").click()
            self.driver.find_element_by_xpath(
                "//button[@id='agregarOtro']").click()
            adjunto = self.driver.find_element_by_xpath(
                "//input[@id='agregarArchivo']")
            adjunto.send_keys(os.path.abspath(os.getcwd()) +
                              '/membretados/' + self.fileName + '.pdf')
            buttons = self.driver.find_elements_by_xpath(
                "//*[contains(text(), 'Guardar envio')]")
            for btn in buttons:
                btn.click()
        self.driver.close()
        