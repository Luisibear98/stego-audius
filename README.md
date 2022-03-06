<div id="top"></div>

[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2017/08/07172624/170727_steganography-0.jpg" alt="Logo" width="400" height="200">
  </a>

  <h3 align="center">Streaming stego</h3>

 
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
    
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project



This is the code for the assignment of the class of APTs and the main Idea is to create a proof of concept of a streaming audio service with stego capabilities.

It consist on:
* Server: Streams the audio and process it in order to embed the secret information.
* Client: Reads and process the audio to recover the hidden information.


The embedding algorithm comes from this <a href="https://www.researchgate.net/publication/281940948_A_Wav-Audio_Steganography_Algorithm_Based_on_Amplitude_Modifying">paper</a> and ensures good audio quality and good hiding of information

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

This project has been completely coded using python.

* [Python](https://www.python.org/downloads/)



<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To be able to deploy this project, please make sure to have python (at least 3.0) and pip3 in order to be able to install and execute all the code,

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* Visit this link and install Python.
  ```sh
  https://www.python.org/downloads/
  ```

* Visit this link and install Python.
  ```sh
  https://pip.pypa.io/en/stable/cli/pip_install/
  ```

### IMPORTANT FOR WINDOWS

To intall PYAUDIO please follow the following:
* first step
  ```sh
  pip install pipwin
  ```

* Second step
  ```sh
  pipwin install pyaudio
  ```
  
  

### Installation

Please follow this intructions to install all code dependencies

1. Clone the repo
   ```sh
   https://github.com/Luisibear98/streaming-stego-through-wav-modulation.git
   ```
2. Install NPM packages
   ```sh
   pip3 install -r requirements.txt
   ```


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

To make use of the code

1. Runs the client.py
   ```sh
    python3 client.py
   ```
2. Runs the server.py
   ```sh
    python3 server.py
   ```
3. Choose the server mode on the prompt.


<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

* Luis Ibáñez Lissen -  100363822@alumnos.uc3m.es
* Alejandro de la Cruz Alvarado - 100383497@alumnos.uc3m.es
* Leonel Jose Peña Gamboa - 100461544@alumnos.uc3m.es

<p align="right">(<a href="#top">back to top</a>)</p>


