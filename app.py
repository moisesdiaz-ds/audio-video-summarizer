from flask import Flask, request, render_template
import os
import subprocess
import datetime

from time import sleep
import openai
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():

    def is_video_file(file_path):
        try:
            video = VideoFileClip(file_path)
            return True
        except Exception as e:
            return False

    def video_to_audio(video_file, audio_file):
        video = VideoFileClip(video_file)
        audio = video.audio
        audio.write_audiofile(audio_file)


    ## Summarize
    def summarize_text(file_path,apikey):

        

        file_path = file_path.replace('\\','/').replace('uploads','audio_transcription')+".txt"

        # Define the text to be summarized
        text = open(f"{file_path}", "r",encoding="utf-8").read()

        limit = 6500
        loops = (len(text)//limit)+1
        message_list = []
        for n in range(loops):
            n +=1
            if (n!=loops) or (n==1):
                t = text[(n-1)*limit:n*limit]
            else:
                t = text[(n-1)*limit:]

            # Define the prompt for summarization
            #prompt = f"El siguiente texto es una conversacion, porfavor resumelo y enumera los puntos mas importantes, es importante que no falte ningun tema mencionado:\n\n{t}"
            prompt = f"""
            Haz todo lo posible por desarrollar el siguiente texto como si fuera una minuta. Tomando como guia el siguiente ejemplo. Es importante ENUMERAR y DESARROLLAR a plenitud cada uno de los temas

            Texto:
            pero si aquí tú no puedes controlar que te depositen bien la basura porque el tema ese
            tema mira te voy a te voy a desmenuzar la realidad de los hechos es verdad que tú no sabes quién es
            que te la está poniendo pero por eso yo te estoy diciendo a ti que hay tres poros y posibles
            infractores la que está al lado del b201 que la del b202 y lo 2 que están al frente entonces
            usted agarra usted les manda una comunicación a eso 3 con la foto y le dice que nosotros vamos
            a comenzar a ver porque eso ahí no es para poner basura o sea ellos tienen espacio donde poner la
            basura pero es mejor ponerla en el medio de la escalera porque los otros dos tienen una tienen
            un espacio afuera de la puertecita de que sale de ellos que como un balconcito en cosa y la otra
            tiene el espacio para poner la basura del lado de ella porque esas sitios tienen como unos cositos
            en cemento donde tú puedes colocar la basura pero la gente no la quiere tener del lado de la
            puerta es mejor tener la frente a la puerta del otro y eso es lo primero inclusive ahí salió una
            dueña donde le dijo a y que ese era el sitio de poner la basura donde aquí todos sabemos que ese
            no es el sitio de poner la basura porque ese es el medio y es el frente de la puerta de ella es lo
            primero entonces aquí tenemos un supervisor tenemos una administración entonces lo correcto
            es que se haga una comunicación y se les mande a esas tres unidades con la advertencia porque hay
            que darle la advertencia o sea no soy yo como condomine la que tiene que hacer la gestión porque
            para eso que nosotros estamos pagando una administración porque si no entonces vamos a
            quitar la administración y vamos a sentarnos nosotros vamos a poner grupos de supervisión y
            de apoyo y trabajemos y ganemos nuestro cuarto entonces aquí todo el mundo como le dije el otro
            día tiene que saber lo que le toca entonces de los parqueos es lo mismo el infractor está ahí en el
            b entonces hay que mandarlo una comunicación a todos y decirle este apartamento está ocupado y
            ustedes saben que no pueden estar tomando parqueos ajenos es que no pueden entonces si aquí está si
            si aquí entre el que le da la gana por la puerta y todavía nosotros no hemos podido resolver ese
            problema de la puerta aquí todo el mundo hace lo que tú te crees que tú vas a poder regular y tú
            vas a poder hacer un censo y ve cuánta gente tiene parqueo y quién se roba un parqueo y quién no lo
            correcto es porque nosotros sí sabemos cuando una gente se muda lo correcto es que cuando una gente
            se mude ahí inmediatamente haya un cono un cono o una cosa dura que se le ponga en el medio puesta
            por nosotros mismos por la administración que nosotros lo podemos hacer y que ese cono solo
            lo mueva el que está en cosa ponerse de acuerdo con el que se va aquí no se puede parquear ya
            esto de quien movió desde que se ve por la cámara quien movió ese cono y papá qué hace voy pregunto
            de quién el vehículo una infracción pero eso hay que tener voluntad y darle seguimiento a la cosa
            pero aquí no aquí todo es al calor de los hechos cuando explota la bomba es que queremos hay después
            que la gente ya se explota y se rebosa y dice de todo ahí es que hay que salimos a buscar y esa
            no es la función ni de la administración ni de la junta directiva es preveer las cosas y trabajar
            con tiempo para evitar situaciones porque la gente después se jarta se jarta y le pierde el respeto


            Resumen:
            Tema de la basura:
                Se discutió el tema de la basura y se concluyó que se debe tomar acción para evitar que los infractores sigan colocando la basura en el medio de la escalera. Se acordó enviar una comunicación a las tres unidades identificadas como posibles infractores, con una foto de la situación y una advertencia de que se tomarán medidas si continúa la situación. Se reiteró que la administración debe tomar la responsabilidad de realizar estas acciones y se acordó que se dará seguimiento a la situación.

            Tema de los parqueos:
                Se discutió el tema de los parqueos y se acordó enviar una comunicación a todos los residentes, recordando que no está permitido tomar parqueos ajenos. Se identificó una unidad específica como infractora y se acordó enviar una comunicación a esa unidad para informarles de que deben dejar de ocupar parqueos ajenos. Se discutió la posibilidad de implementar un sistema de conos o señalización para evitar que los residentes ocupen parqueos ajenos y se acordó darle seguimiento a esta propuesta.

            Varios:
                Se discutieron varios asuntos menores y se acordó establecer plazos y responsables para su resolución. Se reiteró la importancia de prever situaciones para evitar conflictos y se acordó que la administración debe tomar la responsabilidad de liderar estas acciones.

            -------------------------------------------

            Texto:
            {t}


            Resumen:
            """


            # Generate a summary
            model_engine = "gpt-3.5-turbo"
            completions = openai.ChatCompletion.create(model=model_engine, messages=[
                    {"role": "system", "content": "Tu eres un asistente muy servicial."},
                    {"role": "user", "content":prompt}])
            message =completions.choices[0].message.content
            message_list.append(message)


        if len(message_list)==1:
            message_final = "".join(message_list)

        else:
            t2 = "\n\n".join(message_list)
            # Define the prompt for summarization
            #prompt = f"Porfavor combina estos {len(message_list)} resumenes en uno solo y los puntos enumerados en una sola lista, es importante que no falte ningun tema mencionado:\n\n{t2}"

            prompt = f"""
            Haz todo lo posible por desarrollar los siguientes resumenes como si fueran una minuta. Tomando como guia el siguiente ejemplo. Es importante ENUMERAR y DESARROLLAR a plenitud cada uno de los temas

            Texto:
            pero si aquí tú no puedes controlar que te depositen bien la basura porque el tema ese
            tema mira te voy a te voy a desmenuzar la realidad de los hechos es verdad que tú no sabes quién es
            que te la está poniendo pero por eso yo te estoy diciendo a ti que hay tres poros y posibles
            infractores la que está al lado del b201 que la del b202 y lo 2 que están al frente entonces
            usted agarra usted les manda una comunicación a eso 3 con la foto y le dice que nosotros vamos
            a comenzar a ver porque eso ahí no es para poner basura o sea ellos tienen espacio donde poner la
            basura pero es mejor ponerla en el medio de la escalera porque los otros dos tienen una tienen
            un espacio afuera de la puertecita de que sale de ellos que como un balconcito en cosa y la otra
            tiene el espacio para poner la basura del lado de ella porque esas sitios tienen como unos cositos
            en cemento donde tú puedes colocar la basura pero la gente no la quiere tener del lado de la
            puerta es mejor tener la frente a la puerta del otro y eso es lo primero inclusive ahí salió una
            dueña donde le dijo a y que ese era el sitio de poner la basura donde aquí todos sabemos que ese
            no es el sitio de poner la basura porque ese es el medio y es el frente de la puerta de ella es lo
            primero entonces aquí tenemos un supervisor tenemos una administración entonces lo correcto
            es que se haga una comunicación y se les mande a esas tres unidades con la advertencia porque hay
            que darle la advertencia o sea no soy yo como condomine la que tiene que hacer la gestión porque
            para eso que nosotros estamos pagando una administración porque si no entonces vamos a
            quitar la administración y vamos a sentarnos nosotros vamos a poner grupos de supervisión y
            de apoyo y trabajemos y ganemos nuestro cuarto entonces aquí todo el mundo como le dije el otro
            día tiene que saber lo que le toca entonces de los parqueos es lo mismo el infractor está ahí en el
            b entonces hay que mandarlo una comunicación a todos y decirle este apartamento está ocupado y
            ustedes saben que no pueden estar tomando parqueos ajenos es que no pueden entonces si aquí está si
            si aquí entre el que le da la gana por la puerta y todavía nosotros no hemos podido resolver ese
            problema de la puerta aquí todo el mundo hace lo que tú te crees que tú vas a poder regular y tú
            vas a poder hacer un censo y ve cuánta gente tiene parqueo y quién se roba un parqueo y quién no lo
            correcto es porque nosotros sí sabemos cuando una gente se muda lo correcto es que cuando una gente
            se mude ahí inmediatamente haya un cono un cono o una cosa dura que se le ponga en el medio puesta
            por nosotros mismos por la administración que nosotros lo podemos hacer y que ese cono solo
            lo mueva el que está en cosa ponerse de acuerdo con el que se va aquí no se puede parquear ya
            esto de quien movió desde que se ve por la cámara quien movió ese cono y papá qué hace voy pregunto
            de quién el vehículo una infracción pero eso hay que tener voluntad y darle seguimiento a la cosa
            pero aquí no aquí todo es al calor de los hechos cuando explota la bomba es que queremos hay después
            que la gente ya se explota y se rebosa y dice de todo ahí es que hay que salimos a buscar y esa
            no es la función ni de la administración ni de la junta directiva es preveer las cosas y trabajar
            con tiempo para evitar situaciones porque la gente después se jarta se jarta y le pierde el respeto


            Resumen:
            Tema de la basura:
                Se discutió el tema de la basura y se concluyó que se debe tomar acción para evitar que los infractores sigan colocando la basura en el medio de la escalera. Se acordó enviar una comunicación a las tres unidades identificadas como posibles infractores, con una foto de la situación y una advertencia de que se tomarán medidas si continúa la situación. Se reiteró que la administración debe tomar la responsabilidad de realizar estas acciones y se acordó que se dará seguimiento a la situación.

            Tema de los parqueos:
                Se discutió el tema de los parqueos y se acordó enviar una comunicación a todos los residentes, recordando que no está permitido tomar parqueos ajenos. Se identificó una unidad específica como infractora y se acordó enviar una comunicación a esa unidad para informarles de que deben dejar de ocupar parqueos ajenos. Se discutió la posibilidad de implementar un sistema de conos o señalización para evitar que los residentes ocupen parqueos ajenos y se acordó darle seguimiento a esta propuesta.

            Varios:
                Se discutieron varios asuntos menores y se acordó establecer plazos y responsables para su resolución. Se reiteró la importancia de prever situaciones para evitar conflictos y se acordó que la administración debe tomar la responsabilidad de liderar estas acciones.

            -------------------------------------------

            Texto:
            {t2}


            Resumen:
            """

            # Generate a summary
            model_engine = "gpt-3.5-turbo"
            completions = openai.ChatCompletion.create(model=model_engine, messages=[
                    {"role": "system", "content": "Tu eres un asistente muy servicial."},
                    {"role": "user", "content":prompt}])
            message_final =completions.choices[0].message.content

        with open(f"results/{file_path.split('.')[0]}.txt".split('\\')[-1].split('/')[-1], 'w') as f:
            f.write(message_final)

        print(message_final)

            
        return message_final


        
    # Apply API key
    apikey = open("../api-key.txt", "r").read().replace("\n","")
    
    openai.api_key = apikey

    file = request.files['file']
    uploads_dir = os.path.join(app.root_path, "uploads")
    filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + file.filename
    file_path = os.path.join(uploads_dir, filename)
    file.save(file_path)

    if filename.endswith('ogg'):
        ogg_file = AudioSegment.from_file(file_path, format="ogg")
        new_file_path = "".join(file_path.split(".")[:-1])+".mp3"
        ogg_file.export(new_file_path, format="mp3")
        file_path = new_file_path
        filename = file_path.split('\\')[-1].split('/')[-1]
        print(filename)

    if is_video_file(file_path):
        new_file_path = "".join(file_path.split(".")[:-1])+".mp3"
        video_to_audio(file_path, new_file_path)
        file_path = new_file_path
        filename = file_path.split('\\')[-1].split('/')[-1]

    # VERSION WHISPER GPU LOCAL
    #command = f"whisper {file_path} --task transcribe --model medium --verbose False --device cuda --output_dir audio_transcription"
    #subprocess.run(command, shell=True)

    # VERSION WHISPER API
    audio_file= open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    transcript = transcript['text']

    with open("audio_transcription/"+filename+".txt", 'w',encoding="utf-8") as f:
        f.write(transcript)

    try:
        message_final = summarize_text(file_path,apikey)
    except Exception as e:
        print('Se intentara de nuevo, hubo un problema de tipo ', e)
        sleep(3)
        try:
            message_final = summarize_text(file_path,apikey)
        except Exception as e:
            print('Otra vez, hubo un problema de tipo ', e)


    message_final = message_final.replace("\n", "<br>")
    return render_template('received.html', message_final=message_final)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    #app.run()
