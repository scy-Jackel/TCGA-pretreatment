import os
import openslide
import numpy as np
from PIL import Image
from concurrent.futures import ProcessPoolExecutor


def create_subfolder(base_path, folder_name):
    subfolder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
    return subfolder_path


def save_subimage(args):
    svs_file_path, x, y, size, subfolder_path = args
    slide = openslide.OpenSlide(svs_file_path)

    # 读取区域
    region = slide.read_region((x, y), 0, (size, size))
    region = region.convert("RGB")

    region_width, region_height = region.size

    # 第一个条件：检查尺寸是否足够
    if region_width < 448 or region_height < 448:
        # print(f"Skipped subimage at {x}, {y} due to size constraint.")
        slide.close()
        return

    # 计算子图中病理组织的面积
    tissue_area = calculate_tissue_area(region)

    # 第二个条件：检查病理组织面积是否足够
    subimage_area = region_width * region_height
    # if tissue_area == 0:
    #     # print(f"Skipped subimage at {x}, {y} due to background area constraint.")
    #     slide.close()
    #     return

    if tissue_area < (subimage_area * 0.6):
        # print(f"Skipped subimage at {x}, {y} due to tissue area constraint.")
        pass
    else:
        region.save(os.path.join(subfolder_path, f"{x}_{y}.png"))
        # print(f"Saved subimage at {x}, {y}")

    slide.close()


def process_folder(folder_name, root_folder, output_folder):
    folder_path = os.path.join(root_folder, folder_name)
    svs_files = [f for f in os.listdir(folder_path) if f.endswith('.svs')]
    if svs_files:
        svs_file_path = os.path.join(folder_path, svs_files[0])
        subfolder_path = create_subfolder(output_folder, folder_name)

        slide = openslide.OpenSlide(svs_file_path)
        width, height = slide.dimensions
        size = 448  # 子图大小

        tasks = []

        for y in range(0, height, size):
            for x in range(0, width, size):
                tasks.append((svs_file_path, x, y, size, subfolder_path))

        # 使用 ProcessPoolExecutor 并行处理子图
        with ProcessPoolExecutor() as executor:
            executor.map(save_subimage, tasks)

        slide.close()
    else:
        print(f"文件夹 '{folder_name}' 中没有 svs 文件。")


def process_svs_files(root_folder, output_folder):
    with ProcessPoolExecutor() as executor:
        for folder_name in os.listdir(root_folder):
            if os.path.isdir(os.path.join(root_folder, folder_name)):
                executor.submit(process_folder, folder_name, root_folder, output_folder)


def calculate_tissue_area(region):
    np_region = np.array(region)

    # 使用一个阈值小于200来检测病理组织
    threshold_tissue = 200  # 病理组织阈值
    mask_tissue = np.mean(np_region, axis=2) < threshold_tissue  # 病理组织掩码
    tissue_area = np.sum(mask_tissue)  # 病理组织面积

    # 新增条件：检查均值小于10的面积
    threshold_background = 10  # 背景阈值
    mask_background = np.mean(np_region, axis=2) < threshold_background  # 背景掩码
    background_area = np.sum(mask_background)  # 背景面积

    # 计算区域总面积
    subimage_area = np_region.shape[0] * np_region.shape[1]

    # 判断均值小于10的面积是否超过20%
    if background_area > (subimage_area * 0.2):
        # print("Skipped subimage due to background area exceeding 20%")
        return 0  # 返回0表示不保存图像

    return tissue_area


if __name__ == "__main__":
    root_folder = r"E:\TCGA"
    output_folder = r"H:\TCGA_sub"
    process_svs_files(root_folder, output_folder)
