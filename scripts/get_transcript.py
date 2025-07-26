import sys
import json
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

def get_youtube_transcript(video_id, languages=['pt', 'en']):
    """
    Busca a transcrição de um vídeo do YouTube.
    Prioriza idiomas na lista 'languages' (ex: português, depois inglês).
    Retorna a transcrição como texto simples ou um objeto de erro em JSON.
    """
    try:
        # Lista as transcrições disponíveis para o vídeo
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Tenta encontrar a transcrição no idioma especificado, seguindo a prioridade
        transcript = None
        for lang_code in languages:
            try:
                transcript = transcript_list.find_transcript([lang_code])
                break # Se encontrar, usa essa e sai do loop
            except NoTranscriptFound:
                continue # Tenta o próximo idioma
        
        if transcript is None:
            # Se nenhum idioma da lista for encontrado, tenta o primeiro disponível
            # Isso pode ser útil se o vídeo tiver legendas em um idioma não esperado
            try:
                transcript = transcript_list.find_transcript(transcript_list.find_available_languages())
            except NoTranscriptFound:
                raise NoTranscriptFound(video_id) # Realmente não há transcrição

        # Obtém o conteúdo da transcrição
        fetched_transcript = transcript.fetch()

        # Combina os trechos de texto em uma única string
        full_text = " ".join([item['text'] for item in fetched_transcript])
        
        # Retorna o resultado como JSON para fácil parseamento no n8n
        return {"transcript": full_text, "video_id": video_id, "language": transcript.language_code}
    except NoTranscriptFound:
        return {"error": f"Nenhuma transcrição encontrada para o vídeo ID: {video_id} nos idiomas especificados ou disponíveis.", "video_id": video_id}
    except TranscriptsDisabled:
        return {"error": f"As transcrições estão desabilitadas para o vídeo ID: {video_id}.", "video_id": video_id}
    except Exception as e:
        return {"error": f"Ocorreu um erro inesperado: {str(e)}", "video_id": video_id}

if __name__ == "__main__":
    # O script espera o ID do vídeo como primeiro argumento de linha de comando
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Por favor, forneça o ID de um vídeo do YouTube como argumento."}))
        sys.exit(1)
    
    video_id = sys.argv[1]
    result = get_youtube_transcript(video_id)
    print(json.dumps(result))
