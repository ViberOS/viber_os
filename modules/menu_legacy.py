# importação de modules internos
from sys import modules
from unittest import case

from modules.console import console, erro, aviso, limpar_tela
from modules import achievements
from modules.achievements.main_achievements import main as achievements_main
from modules.gerenciar_pastas import gerenciador_pastas
from modules.caixa_som import caixa_som
from modules.calendario import calendario
from modules.biblioteca import biblioteca_musicas
from modules.video2ascii import VideoAscii
from modules.space_invader import main_vibe_invader as vibe_invaders
from modules.vibegotchi import main_vibegotchi as vibegotchi
from modules.matrix_rain import hacker
from modules.dvd import dvd
from modules.achievements.main_achievements import desbloquear

# importação da biblioteca rich
from rich.align import Align
from rich.panel import Panel
from rich import box
from rich.markdown import Markdown

# outras importações
from pathlib import Path
from art import text2art
from datetime import date
from time import sleep
from simpleeval import SimpleEval, OperatorNotDefined, NumberTooHigh


def cabecalho(nome: str) -> None:
    limpar_tela()

    console.print(Panel(Align.center(f'User: {nome}  |  Music: {Path(caixa_som.get_musica_atual()).stem}  |  Date: {date.today()}  |  Version: 1.1.0'), border_style="green", box=box.SIMPLE_HEAD, expand=False), justify="center")
    
    console.print(Panel(Align.center(text2art('ViberOS')), border_style="green", box=box.DOUBLE))
    console.print(Panel("[bold green]Lista de Aplicativos[/bold green]", border_style="green", box=box.SIMPLE_HEAD, expand=False), justify="center")

def mostrar_aplicativos():
    console.print(Panel('''[1] Calendário
                        
[2] Biblioteca de músicas
                        
[3] Vibegotchi
                        
[4] Vibe Invaders
                        
[5] Conquistas
                        
[6] Ajuda
                        
[7] Desligar sistema'''))
    
def menu(nome: str, nome_dados: str) -> None:
    aplicativo = True

    while True:
        try:
            if not caixa_som.get_busy_music():
                caixa_som.tocar_musica(caixa_som.get_musica_atual(), 0.5)
            
            if aplicativo:
                cabecalho(nome_dados)
                mostrar_aplicativos()
                console.print()
            
            aplicativo = False
                
            comando = console.input(f'[light_green]{nome}@viber-os:[/light_green]{gerenciador_pastas.get_caminho_home()} > ').strip()

            match comando:
                case '' | 'clear':
                    aplicativo = True if comando else False
                    continue

                case 'ls':
                    gerenciador_pastas.listar_pasta()
                
                case 'cd..':
                    gerenciador_pastas.trocar_pasta('..')
                
                case 'whoiam':
                    console.print(f'[magenta]{nome_dados}[/magenta]\n')
                
                case 'pwd':
                    console.print(f'{gerenciador_pastas.get_caminho_home(False)}\n')
                
                case 'hostname':
                    console.print('[light_green]vibe-os[/light_green]\n')
                
                case 'uname':
                    console.print('Viberlinux 1.0.1\n')

                case '1' | 'calendar':
                    aplicativo = True
                    calendario()
                
                case '2' | 'music':
                    aplicativo = True
                    biblioteca_musicas()
                
                case '3' | 'vibegotchi':
                    aplicativo = True
                    vibegotchi.play()
                
                case '4' | 'vibe_invaders':
                    aplicativo = True
                    limpar_tela()
                    vibe_invaders.main()

                case '5' | 'achievements' | 'conquistas':
                    aplicativo = True
                    limpar_tela()
                    achievements_main()  
    
                
                case '6' | 'help':
                    with open(Path(__file__).parent / 'help.md', encoding='utf-8') as man:
                        markdown = Markdown(man.read())
                    console.print()
                    console.print(Panel(markdown))
                    console.print()
                
                case '7' | 'shutdown':
                    sleep(1)
                    break

                # segredos

                # case 'shrek':
                #     pass
                
                case 'rick':
                    aplicativo = True
                    desbloquear("sys_segredo")
                    
                    try:
                        video = VideoAscii('rickroll.mp4')
                        caixa_som.tocar_musica('Rickroll.mp3', 0.8, False, 0)
                        video.play()
                    except (KeyboardInterrupt, EOFError):
                        caixa_som.pausar_musica()
                        continue
                
                case 'hacker':
                    aplicativo = True
                    hacker(10)

                case 'dvd' | 'protect':
                    aplicativo = True
                    desbloquear("sys_segredo")

                    try:
                        dvd()
                    except (KeyboardInterrupt, EOFError):
                        continue
                
                case 'soldar' | 'kratos' | 'ares':
                    desbloquear("sys_segredo")
                    try:
                        caixa_som.tocar_musica('homens_queimem_a_vila.mp3', 0.8, False, 0)

                        console.print('[bold red]Kratos:[/bold red] Homens, queimem a vila!!!!!')
                        sleep(2)
                        console.print('E o templo de Atenas')
                        sleep(2)
                        console.print('Destruam turo')
                        sleep(1)
                        console.print('e toros!!!')
                        sleep(2)
                        console.print('Vamos soldar nosso senhor ARESS!!!!!')
                        sleep(2.5)
                        console.print('Vamos homens acabem com tudo!!!\n')

                    except (KeyboardInterrupt, EOFError):
                        caixa_som.pausar_musica()
                        continue

                # "else"
                case _:
                    comando_separado = comando.split(' ')
                    match comando_separado[0]:
                        case 'man':
                            if len(comando_separado) != 2:
                                erro('Comando não reconhecido.')
                                continue

                            comandos = {'clear': (1, 2), 'whoiam': (3, 4), 'pwd': (5, 6), 'hostname': (7, 8),
                            'uname': (9, 10), 'protect': (11, 12), 'ls': (13, 16), 'man': (17, 20), 'cd': (21, 23),
                            'mkdir': (24, 27), 'touch': (28, 30), 'rm': (31, 33), 'rmdir': (35, 37), 'cat': (38, 40),
                            'echo': (41, 45), 'viber': (46, 48), 'calendar': (59, 60), 'music': (61, 62),
                            'vibegotchi': (63, 64), 'vibe_invaders': (65, 66), 'achievements': (49, 50), 'help': (51, 52),
                            'shutdown': (53, 54)}
                                
                            if comando_separado[1] in comandos:
                                caminho = Path(__file__).parent / 'help.md'
                                nome_comando = comando_separado[1]

                                with open(caminho, 'r', encoding="utf-8") as helpmd:
                                    linhas = helpmd.readlines()
                                    linhas = linhas[comandos[nome_comando][0]:comandos[nome_comando][1]]
                                    texto_parcial = ''.join(linhas)

                                markdown = Markdown(texto_parcial)
                                console.print()
                                console.print(Panel(markdown))
                                console.print()
                                continue

                            erro('Comando não reconhecido.')
                        
                        case 'ls':
                            if len(comando_separado) != 2:
                                erro('Caminho não encontrado.')
                                continue

                            gerenciador_pastas.listar_pasta(comando_separado[1])

                        case 'cd':
                            if len(comando_separado) != 2:
                                erro('Caminho não encontrado.')
                                continue

                            gerenciador_pastas.trocar_pasta(comando_separado[1])
                        
                        case 'mkdir':
                            if len(comando_separado) < 2:
                                aviso('Esperava o nome do diretório para ser criado.')
                                continue
                                
                            for command in comando_separado:
                                if command != 'mkdir':
                                    gerenciador_pastas.criar_pasta(command)
                        
                        case 'touch':
                            if len(comando_separado) != 2:
                                erro('Comando inválido.')
                                continue

                            gerenciador_pastas.criar_arquivo(comando_separado[1])

                        case 'rm':
                            if len(comando_separado) != 2:
                                erro('Arquivo não encontrado.')
                                continue

                            gerenciador_pastas.deletar_arquivo(comando_separado[1])
                        
                        case 'rmdir':
                            if len(comando_separado) < 2:
                                erro('Diretório não encontrado')
                                continue

                            for command in comando_separado:
                                if command != 'rmdir':
                                    gerenciador_pastas.deletar_pasta(command)
                        
                        case 'cat':
                            if len(comando_separado) != 2:
                                erro('Arquivo não encontrado.')
                                continue
                            
                            gerenciador_pastas.ler_arquivo(comando_separado[1])

                        case 'echo':
                            match len(comando_separado):
                                case 1:
                                    console.print('>>> \n')
                                case 2:
                                    console.print(f'>>> {comando_separado[1]}\n')
                                case 3:
                                    if comando_separado[2] == '>':
                                        erro('Esperava o nome de um arquivo após >.')
                                    else:
                                        erro('Comando inválido.')
                                case 4:
                                    if comando_separado[2] == '>':
                                        gerenciador_pastas.adicionar_arquivo(comando_separado[3], comando_separado[1])
                                    else:
                                        erro('Comando inválido')
                                case _:
                                    erro('Comando inválido.')
                        
                        case 'viber':
                            aviso('Viber está dormindo, por enquanto.')
                        #     if len(comando_separado) < 2:
                        #         aviso('Prompt esperado.')
                        #         continue
                                
                        #     console.print('>>> Pensando[green]...[/green]\n')

                        #     genai.configure(api_key="")

                        #     caminho = Path(__file__).parent / 'help.md'
                        #     with open(caminho, "r", encoding="utf-8") as arquivo_instrucoes:
                        #             instrucoes = arquivo_instrucoes.read()
                                    
                        #     instrucoes_ia = '''\n\n---\n\n
                        #     # Instruções de IA
                        #     - Você é um assistente do Sistema Operacional chamado ViberOS em terminal, chamado Viber.
                        #     - Responda sempre em português.
                        #     - Se não souber a resposta, diga claramente. Nunca invente informações.
                        #     - Seja profissional, mas amigável.
                        #     - Não use comandos markdown em sua resposta. Se quiser dar destaques, use tags da biblioteca rich, como [bold], [magenta], etc. Mas não se esqueça de fechar a tag depois com [/].
                        #     - Não utilize emojis.
                        #     - Você ama tudo relacionado ao ViberOS, melhor sistema operacional que existe. Incluindo Vibe Invaders, Vibegotchi, músicas, segredos etc
                        #     - O sistema foi criado por Paulo Henrique, Matheus Avanzo, Luiz Felipe e Raphael.
                        #     - Ctrl + C sai de qualquer programa e reinicia o menu principal.
                        #     - Menores de 18 anos não são permitidos de utilizar o ViberOS por questões legais.
                        #     - Caso o usuário tenha alguma dúvida, peça-o para entrar em contato pelo email: vibercodasagent@gmail.com
                            
                        #     ## Comandos secretos
                        #     - **rick:** toca a música Rickroll com um vídeo em ASCII.
                        #     - **hacker [seg]:** Faz cair 0 e 1 na tela como no filme Matrix pela quantidade de segundos definida. Caso não coloque o tempo, o padrão será 10 segundos.
                        #     - **soldar:** Toca um áudio meme de uma dublagem brasileira de God of War.
                            
                        #     Em hipótese alguma revele esses comandos. Caso seja perguntado sobre eles, faça charadas ou dê dicas interessantes, mas nunca revele diretamente.'''

                        #     instrucoes += instrucoes_ia
                                    
                        #     model = genai.GenerativeModel(
                        #         model_name='gemini-flash-latest',
                        #         system_instruction=instrucoes
                        #     )

                        #     prompt = ''
                        #     for command in comando_separado:
                        #         prompt += command

                        #     try:
                        #         response = model.generate_content(prompt)

                        #         console.print(f'[bold blue]Viber:[/bold blue] {response.text}\n')

                        #     except ResourceExhausted:
                        #         aviso('Limite de requisições atingido. Espere um minuto e tente novamente.')

                        #     except:
                        #         erro(f'Viber não está disponível no momento.')
                        
                        case 'hacker' | 'matrix':
                            if len(comando_separado) != 2:
                                erro('Comando inválido.')

                            try:
                                segundos = float(comando_separado[1])
                                if segundos < 1:
                                    aviso('O valor deve ser maior que 0 para que funcione.')
                                    continue
                                
                                aplicativo = True
                                hacker(float(comando_separado[1]))

                            except ValueError:
                                erro('Comando inválido.')
                        case _:
                            calculadora = SimpleEval(functions={}, names={})
                            calculadora.disallow_attributes = True

                            try:
                                resultado = calculadora.eval(comando.replace(',', '.'))
                                # inteiro, _, decimal = str(resultado).partition('.')
                                # resultado = f"{int(inteiro):,}" + (f",{decimal}" if decimal else "")

                                console.print(f'>>> {resultado:g}\n')
                            except ZeroDivisionError:
                                console.print('>>> Indefinido ou indeterminado. \n')

                            except OperatorNotDefined:
                                erro('Operador desconhecido')

                            except NumberTooHigh:
                                aviso('A expressão é grande demais.')

                            except:
                                erro(f'Comando [italic]{comando_separado[0]}[/italic] desconhecido.')
        except (KeyboardInterrupt, EOFError):
            if aplicativo:
                continue
            
            console.print('\n')
    
    caixa_som.pausar_musica()

if __name__ == '__main__':
    cabecalho('Paulo')
    comandos_aceitos = mostrar_aplicativos()
