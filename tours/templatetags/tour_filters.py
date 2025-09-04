from django import template

register = template.Library()

@register.filter
def youtube_embed(url):
    """Преобразует YouTube URL в embed URL"""
    if not url or not isinstance(url, str):
        return ""
    
    # Очищаем URL от лишних пробелов
    url = url.strip()
    
    # Если уже embed URL, возвращаем как есть
    if 'embed/' in url and 'youtube.com' in url:
        return url
    
    # Извлекаем video ID из различных форматов YouTube URL
    video_id = None
    
    try:
        # Формат: https://www.youtube.com/watch?v=VIDEO_ID
        if 'watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0].split('#')[0]
        # Формат: https://youtu.be/VIDEO_ID
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0].split('#')[0]
        # Формат: https://www.youtube.com/embed/VIDEO_ID
        elif 'embed/' in url:
            video_id = url.split('embed/')[1].split('?')[0].split('#')[0]
        
        # Проверяем, что video_id валидный (обычно 11 символов)
        if video_id and len(video_id) == 11 and video_id.replace('-', '').replace('_', '').isalnum():
            return f"https://www.youtube.com/embed/{video_id}"
        
    except (IndexError, AttributeError):
        pass
    
    # Если не удалось извлечь video_id, возвращаем пустую строку
    return ""
