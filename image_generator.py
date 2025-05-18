import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import textwrap
import math
import os
from datetime import datetime, timedelta
from PIL import Image

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

def generate_disruption_images(disruptions, output_dir="output", rows_per_page=6):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    wrapped_data = []
    for row in disruptions:
        timestamp = str(row['timestamp'])
        if " bis " in timestamp:
            timestamp = timestamp.replace(" bis ", "\nbis ")

        wrapped_row = [
            "\n" + "\n".join(textwrap.wrap(str(row['data-lines']), 20)) + "\n",
            "\n" + "\n".join(textwrap.wrap(str(row['title']), 20)) + "\n",
            "\n" + "\n".join(textwrap.wrap(timestamp, 20)) + "\n",
            "\n" + "\n".join(textwrap.wrap(str(row['reason']), 20)) + "\n",
        ]
        wrapped_data.append(wrapped_row)

    num_pages = math.ceil(len(wrapped_data) / rows_per_page)
    image_paths = []

    generated_on = datetime.today().strftime('%d %b %Y')
    valid_for = (datetime.today() + timedelta(days=1)).strftime('%d %b %Y')

    emoji_font = None
    for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
        if "seguiemj" in font.lower():  # Segoe UI Emoji font file
            emoji_font = font
            break
    
    for i in range(num_pages):
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('#f5f5f5')
        ax.axis('off')

        if emoji_font:
            fig.text(
                0.5, 0.96, f"🔮 Disruptions Valid for: {valid_for}",
                ha='center', fontsize=16, weight='bold', color='#333',
                fontproperties=fm.FontProperties(fname=emoji_font)
            )
        else:
            fig.text(
                0.5, 0.96, f"🔮 Disruptions Valid for: {valid_for}",
                ha='center', fontsize=16, weight='bold', color='#333'
            )

        start = i * rows_per_page
        end = start + rows_per_page
        page_data = [["Lines", "Title", "Timestamp", "Reason"]] + wrapped_data[start:end]

        table = ax.table(cellText=page_data, colLabels=None, cellLoc='left', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1, 6)

        for idx, cell in table.get_celld().items():
            cell.set_edgecolor('#dddddd')
            cell.get_text().set_wrap(True)

            if idx[0] == 0:
                cell.set_facecolor('#007ac2')
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

        footer_text = f"📆 Generated: {generated_on}     📄 Page {i+1} of {num_pages}"
        if emoji_font:
            fig.text(
                0.5, 0.02, footer_text,
                ha='center', fontsize=12, color='#555',
                fontproperties=fm.FontProperties(fname=emoji_font)
            )
        else:
            fig.text(
                0.5, 0.02, footer_text,
                ha='center', fontsize=12, color='#555'
            )
            
        filename = os.path.join(output_dir, f"disruptions_page_{i+1}.png")
        fig.savefig(filename, bbox_inches='tight', dpi=300)
        plt.close(fig)
        image_paths.append(filename)

    return image_paths