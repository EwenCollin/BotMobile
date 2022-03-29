# Documentation de BotMobile

## Introduction

BotMobile est un projet de voiture autonome échelle 1:10 conçu dans le cadre de l'UE d'ingénierie du semestre 6 de la licence Sciences et Technologies "Institut Villebon - Georges Charpak" de l'université Paris-Saclay.

Cette voiture autonome (appelée parfois dans le reste de ce document "BotMobile") est l'une des participantes de la Course de voitures autonomes de Paris-Saclay organisée par Anthony Juton.

## Caractéristiques techniques

Cette voiture utilise un châssis/moteur Tamiya TT02 et une batterie NiMH 7,2V 4Ah.
Elle dispose d'un convertisseur DC/DC pour utiliser un courant électrique de 5V afin d'alimenter le Raspberry Pi.

Elle utilise un Raspberry Pi 4 - 8Go RAM avec une carte SD de 16 Go sur laquelle a été installé Raspbian OS x64.

La BotMobile voit le monde au travers d'un RPLidar A2M8 connecté en USB au Raspberry Pi.

La direction et la puissance moteur son contrôlés via PWM en utilisant deux PINs compatibles du Raspberry Pi.

## Contrôle Autonome de la BotMobile

### Introduction

L'approche développée est une IA "apprentissage renforcé" (reinforcement learning). Cette branche de l'IA se base sur des expériences dans un environnement donné pour améliorer un réseau de neurones qui prend des décisions d'après des observations de ce même environnement.
A chaque étape d'entraînement, on donne des informations à l'IA sur son environnement qu'elle utilise pour prendre une décision. Elle est ensuite récompensée ou sanctionnée pour lui permettre d'ajuster son fonctionnement.

Il existe à ce jour beaucoup de techniques d'apprentissage par renforcement. Nous avons privilégié la PPO (Proximal Policy Optimization) pour sa rapidité d'entraînement, d'autant plus qu'elle s'avère performante pour résoudre des problèmes similaires.

La PPO est l'un des algorithmes disponibles de stable-baselines3, une librairie de reinforcement learning qui utilise PyTorch, nous l'avons donc utilisé pour plus de simplicité.



