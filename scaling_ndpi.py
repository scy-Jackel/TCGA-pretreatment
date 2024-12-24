import os
from PIL import Image
import openslide

def create_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def process_and_resize_image(ndpi_file_path, output_folder, target_size=(4000, 3000), chunk_size=(512, 512)):
    try:
        slide = openslide.OpenSlide(ndpi_file_path)
    except Exception as e:
        print(f"无法打开文件 {ndpi_file_path}: {e}")
        return

    # 获取图像的尺寸
    width, height = slide.dimensions
    print(f"处理文件 {ndpi_file_path}，原始尺寸: {width}x{height}")

    # 计算需要多少块
    chunk_width, chunk_height = chunk_size
    chunks_x = (width + chunk_width - 1) // chunk_width  # 向上取整
    chunks_y = (height + chunk_height - 1) // chunk_height  # 向上取整

    # 创建一个新的空白图像来拼接块
    full_image = Image.new('RGB', target_size)

    # 当前坐标偏移
    x_offset = 0
    y_offset = 0

    for y in range(chunks_y):
        print(f"处理行 {y + 1}/{chunks_y}")
        for x in range(chunks_x):
            # 计算当前块的位置和大小
            x_offset = x * chunk_width
            y_offset = y * chunk_height
            chunk_width_actual = min(chunk_width, width - x_offset)
            chunk_height_actual = min(chunk_height, height - y_offset)

            # 读取块
            try:
                chunk = slide.read_region((x_offset, y_offset), 0, (chunk_width_actual, chunk_height_actual)).convert("RGB")
            except Exception as e:
                print(f"读取块失败 ({x}, {y}): {e}")
                continue

            # 计算放缩后的尺寸
            scale_width = int((chunk_width_actual / width) * target_size[0])
            scale_height = int((chunk_height_actual / height) * target_size[1])

            scale_width2 = int((chunk_width / width) * target_size[0])
            scale_height2 = int((chunk_height / height) * target_size[1])

            # 缩放并粘贴到目标图像上
            if scale_width == 0 or scale_height == 0:
                continue
            chunk_resized = chunk.resize((scale_width, scale_height), Image.LANCZOS)
            full_image.paste(chunk_resized, (x * scale_width2, y * scale_height2))

    # 获取文件名并替换扩展名为 .png
    file_name = os.path.splitext(os.path.basename(ndpi_file_path))[0] + ".png"
    output_path = os.path.join(output_folder, file_name)

    # 保存拼接后的图像
    full_image.save(output_path)
    print(f"已保存图像: {output_path}")

    # 关闭 Slide 对象
    slide.close()

def process_ndpi_files(input_folder, output_folder, target_size=(4000, 3000), chunk_size=(512, 512)):
    create_output_folder(output_folder)

    # 遍历输入文件夹中的所有 NDPI 文件
    ndpi_files = [f for f in os.listdir(input_folder) if f.endswith('.ndpi')]
    if not ndpi_files:
        print("输入文件夹中没有找到 NDPI 文件。")
        return

    for ndpi_file in ndpi_files:
        ndpi_file_path = os.path.join(input_folder, ndpi_file)
        process_and_resize_image(ndpi_file_path, output_folder, target_size, chunk_size)

if __name__ == "__main__":
    input_folder = r"E:\肠癌自有_546\直肠"  # 替换为你的 NDPI 图像所在文件夹路径
    output_folder = r"E:\肠癌自有_546\直肠png"  # 替换为你的输出文件夹路径
    process_ndpi_files(input_folder, output_folder)
