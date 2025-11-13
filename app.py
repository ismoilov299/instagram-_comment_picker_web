import os
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from io import BytesIO
import sys

# Agar instagram_api.py shu papkada bo'lsa:
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from instagram_api import InstagramAPI

app = Flask(__name__, template_folder='.')  # agar index.html aynan shu papkada bo'lsa
CORS(app)

# RapidAPI kalitini muhit o'zgaruvchisidan oling
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '532d0e9edemsh5566c31aceb7163p1343e7jsn11577b0723dd')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'instagram-social-api.p.rapidapi.com')

# InstagramAPI obyekti (async)
api = InstagramAPI(api_key=RAPIDAPI_KEY, api_host=RAPIDAPI_HOST)


def run_async(coro):
    """
    Async coroutine'ni Flask (sync) kontekstida xavfsiz chaqirish.
    - Avvalo asyncio.run() sinab ko'radi.
    - Agar event loop allaqachon ishlayotgan bo'lsa (masalan, test yoki ASGI muhit),
      fallback sifatida yangi loop yaratib run_until_complete ishlatadi.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # event loop allaqachon ishlamoqda -> fallback
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            try:
                loop.close()
            except Exception:
                pass


@app.route('/')
def index():
    # Agar index.html shu papkada joylashgan bo'lsa template_folder='.' bilan ishlaydi.
    return render_template('templates/index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        ok = bool(RAPIDAPI_KEY and RAPIDAPI_KEY != 'YOUR_RAPIDAPI_KEY_HERE')
        # Shuningdek API bilan sinov chaqirig'ini bajarish mumkin:
        api_ok = run_async(api.health_check())
        return jsonify({
            'success': True,
            'rapidapi_key_present': ok,
            'api_responding': bool(api_ok)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/post-info', methods=['POST'])
def get_post_info():
    """
    Frontend'dan kelgan post URL yoki shortcode ni olib,
    instagram_api.get_post_info() ga yuboradi va normalizatsiyalangan JSON qaytaradi.
    """
    try:
        data = request.json or {}
        post_url = (data.get('post_url') or '').strip()
        if not post_url:
            return jsonify({'error': 'Post URL kiritilmagan'}), 400

        post_info = run_async(api.get_post_info(post_url))
        if not post_info:
            return jsonify({'error': 'Post topilmadi yoki API xatosi'}), 404

        return jsonify({'success': True, 'data': post_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/post-comments', methods=['POST'])
def get_post_comments():
    """
    Frontenddan kelgan post URL yoki shortcode bo'yicha commentlarni oladi.
    Max_comments ixtiyoriy.
    """
    try:
        data = request.json or {}
        post_url = (data.get('post_url') or '').strip()
        max_comments = data.get('max_comments', None)

        if not post_url:
            return jsonify({'error': 'Post URL kiritilmagan'}), 400

        # Max_comments int ga o'tkazish
        if max_comments is not None:
            try:
                max_comments = int(max_comments)
                if max_comments <= 0:
                    max_comments = None
            except Exception:
                max_comments = None

        comments = run_async(api.get_post_comments(post_url, max_comments=max_comments))
        if comments is None:
            return jsonify({'error': 'Commentlar olinmadi yoki API xatosi'}), 500

        # Agar items dict list emas bo'lsa, moslashtirish
        if not isinstance(comments, list):
            try:
                comments = list(comments)
            except Exception:
                # qaytariladigan struktura noma'lum bo'lsa, to'g'ridan-to'g'ri qaytaramiz
                return jsonify({'success': True, 'data': comments, 'count': None})

        return jsonify({'success': True, 'data': comments, 'count': len(comments)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-comments-excel', methods=['POST'])
def export_comments_to_excel():
    """
    Frontend yuborgan commentlar ro'yxatini Excel faylga aylantirib yuboradi.
    """
    try:
        data = request.json or {}
        comments = data.get('comments', [])
        post_url = data.get('post_url', 'instagram_post')

        if not comments or not isinstance(comments, list):
            return jsonify({'error': "Commentlar mavjud emas yoki noto'g'ri formatda"}), 400

        # DataFrame yaratish
        df = pd.DataFrame(comments)

        # Ustunlar tartibi (agar mavjud bo'lsa)
        columns_order = ['username', 'full_name', 'text', 'like_count', 'is_verified', 'created_at']
        existing_columns = [c for c in columns_order if c in df.columns]
        if existing_columns:
            df = df[existing_columns]

        # Ustun nomlarini o'zgartirish
        rename_map = {
            'username': 'Username',
            'full_name': "To'liq Ism",
            'text': 'Comment',
            'like_count': 'Like Soni',
            'is_verified': 'Tasdiqlangan',
            'created_at': 'Vaqt'
        }
        df.rename(columns=rename_map, inplace=True)

        # created_at (Vaqt) ustunini o'qiladigan formatga o'tkazish
        if 'Vaqt' in df.columns:
            def _fmt(v):
                if pd.isna(v):
                    return ''
                try:
                    # agar sekund timestamp bo'lsa
                    if isinstance(v, (int, float)):
                        vi = int(v)
                        if vi > 1e12:  # millisecond
                            vi = int(vi / 1000)
                        return datetime.fromtimestamp(vi).strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(v, str) and v.isdigit():
                        vi = int(v)
                        if vi > 1e12:
                            vi = int(vi / 1000)
                        return datetime.fromtimestamp(vi).strftime('%Y-%m-%d %H:%M:%S')
                    parsed = pd.to_datetime(v, errors='coerce')
                    if pd.isna(parsed):
                        return str(v)
                    return parsed.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return str(v)
            df['Vaqt'] = df['Vaqt'].apply(_fmt)

        # Excel yaratish xotirada
        output = BytesIO()
        # openpyxl kerak bo'ladi: pip install openpyxl
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Comments', index=False)
            worksheet = writer.sheets['Comments']

            # ustun kengligini avtomatik sozlash
            for col_cells in worksheet.columns:
                max_length = 0
                column_letter = col_cells[0].column_letter
                for cell in col_cells:
                    try:
                        if cell.value:
                            l = len(str(cell.value))
                            if l > max_length:
                                max_length = l
                    except Exception:
                        pass
                adjusted = min(max_length + 2, 60)
                worksheet.column_dimensions[column_letter].width = adjusted

        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_post = ''.join(ch for ch in post_url if ch.isalnum())[:30] or 'instagram_post'
        filename = f'{safe_post}_comments_{timestamp}.xlsx'

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Development server uchun:
    app.run(debug=True, host='0.0.0.0', port=8000)
