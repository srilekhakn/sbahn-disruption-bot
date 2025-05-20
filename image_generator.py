import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import textwrap
import math
import os
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

logo_path = os.path.join("assets", "sbhan_berlin_alert.png")

LINE_COLORS = {
    "S1": "#ec1e0e", "S2": "#009639", "S3": "#0076c0", "S5": "#e30613",
    "S7": "#a4343a", "S8": "#804998", "S9": "#ffc72c", "S25": "#b0008e",
    "S26": "#00b2a9", "S41": "#ff8c00", "S42": "#ff8c00", "S45": "#89CFF0",
    "S46": "#FFD700", "S47": "#FF69B4", "S75": "#0076c0", "S85": "#6c3483"
}

def determine_font_size(text_length):
    if text_length > 70:
        return 10
    elif text_length > 50:
        return 11
    else:
        return 12

def reason_to_emoji(text):
    text = text.lower()
    if "shuttle service" in text or "replacement" in text:
        return "🚌 "
    elif "time changed" in text or "schedule change" in text or "train service changed" in text:
        return "🔁 "
    elif "platform" in text:
        return "🚦 "
    elif "at night" in text:
        return "🌙 "
    elif "no stop" in text or ">" in text:
        return "📍 "
    elif "info" in text or "note" in text:
        return "ℹ️ "
    else:
        return ""

def generate_disruption_images(disruptions, output_dir="output", rows_per_page=6):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    wrapped_data = []
    for row in disruptions:
        timestamp = str(row['timestamp'])
        if " bis " in timestamp:
            timestamp = timestamp.replace(" bis ", "\nbis ")
        reason_text = str(row['reason'])
        emoji = reason_to_emoji(reason_text)
        reason_with_emoji = f"{emoji}{reason_text}"
        wrapped_row = [
            "\n" + "\n".join(textwrap.wrap(str(row['data-lines']), 20)) + "\n",
            "\n" + "\n".join(textwrap.wrap(str(row['title']), 20)) + "\n",
            "\n" + "\n".join(textwrap.wrap(timestamp, 20)) + "\n",
            "\n" + "\n".join(textwrap.wrap(reason_with_emoji, 20)) + "\n"
        ]
        wrapped_data.append(wrapped_row)

    num_pages = math.ceil(len(wrapped_data) / rows_per_page)
    image_paths = []

    generated_on = datetime.today().strftime('%d %b %Y, %H:%M')
    valid_for = (datetime.today() + timedelta(days=1)).strftime('%d %b %Y')

    emoji_font = None
    for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
        if "seguiemj" in font.lower():
            emoji_font = font
            break

    for i in range(num_pages):
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('#f5f5f5')
        ax.axis('off')
        header_y = 0.98
        header_x = 0.80

        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path).resize((80, 80))
            logo_img = np.array(logo_img)
            imagebox = OffsetImage(logo_img, zoom=1)
            ab = AnnotationBbox(imagebox, (0.02,header_y-0.05), frameon=False, xycoords='axes fraction', box_alignment=(0, 1))
            ax.add_artist(ab)
        ax.text(
            header_x-0.6, header_y-0.1, "Service Notices "+ valid_for,
            ha='left', va='top', fontsize=28, weight='bold', color='#333',
            fontproperties=fm.FontProperties(fname=emoji_font) if emoji_font else None
        )
        
        subtitle_text = f"Construction activity valid for {valid_for} during day time · Sourced from sbahn.berlin"
        ax.text(
            0.05, header_y, subtitle_text,
            ha='left', va='top', fontsize=13, color='#5e6e7e',
            fontproperties=fm.FontProperties(fname=emoji_font) if emoji_font else None
        )
        start = i * rows_per_page
        end = start + rows_per_page
        page_data = [["Lines", "Title", "Timestamp", "Alert"]] + wrapped_data[start:end]

        table = ax.table(
            cellText=page_data,
            colLabels=None,
            cellLoc='left',
            loc=None,
            bbox=[0.01, -0.03, 0.98, 0.80]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(14)

        for idx, cell in table.get_celld().items():
            cell.set_edgecolor('#dddddd')
            cell.get_text().set_wrap(True)
            if emoji_font:
                cell.get_text().set_fontproperties(fm.FontProperties(fname=emoji_font))

            if idx[0] == 0:
                cell.set_facecolor("#1c4313")
                cell.set_text_props(color='white', weight='bold', fontsize=16)
            else:
                cell.set_facecolor('white')
                content_length = len(cell.get_text().get_text())
                cell.get_text().set_fontsize(determine_font_size(content_length))
                if idx[1] == 0:
                    line_code = cell.get_text().get_text().split(",")[0].strip().upper()
                    line_color = LINE_COLORS.get(line_code, "#000000")
                    cell.get_text().set_color(line_color)
                    cell.get_text().set_weight("bold")

        fig.text(
            0.15, 0.02, f"📆 Updated: {generated_on}",
            ha='left', fontsize=12, color='#555',
            fontproperties=fm.FontProperties(fname=emoji_font) if emoji_font else None
            )
        fig.text(
            0.88, 0.02, f"📄 Page {i+1} of {num_pages}",
            ha='right', fontsize=12, color='#555',
            fontproperties=fm.FontProperties(fname=emoji_font) if emoji_font else None
        )
        disclaimer_text = "ℹ️ This is an unofficial summary. Only daytime disruptions are shown. Visit sbahn.berlin for full details."
        
        fig.text(0.14, 0.06, disclaimer_text,ha='left', fontsize=11, color='#888',
        fontproperties=fm.FontProperties(fname=emoji_font) if emoji_font else None)

        filename = os.path.join(output_dir, f"disruptions_page_{i+1}.png")
        fig.savefig(filename, bbox_inches='tight', dpi=250)
        plt.close(fig)
        image_paths.append(filename)

    return image_paths