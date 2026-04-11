"""
Pillow 常用功能学习脚本。

说明：
- 输入图片默认使用 `assets/WechatIMG10.jpeg`
- 输出文件统一写到 `assets/output/` 目录，避免覆盖原图
- 这是学习示例，演示常见 API 用法（打开、保存、缩放、裁剪、旋转、滤镜、绘图、拼图）
"""

from pathlib import Path

from PIL import Image, ImageEnhance, ImageDraw, ImageFilter, ImageOps


# 基础路径：当前文件所在目录（2026-review）
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_IMAGE_PATH = ASSETS_DIR / "WechatIMG10.jpeg"
OUTPUT_DIR = ASSETS_DIR / "output"


def ensure_output_dir() -> Path:
    """
    确保输出目录存在。

    Returns:
        Path: 输出目录路径（assets/output）。

    逻辑说明：
        - Pillow 的 save 需要目标目录先存在。
        - 这里统一在每个示例前保证目录创建完成，避免重复判断。
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def show_image_info(image_path: Path = DEFAULT_IMAGE_PATH) -> None:
    """
    读取并打印图片基础信息。

    Args:
        image_path (Path): 要读取的图片路径。

    Returns:
        None

    逻辑说明：
        - 使用 `Image.open` 打开图片。
        - 打印常见属性：格式、尺寸、颜色模式、EXIF 是否存在。
    """
    with Image.open(image_path) as img:
        print("=== Image Info ===")
        print("path:", image_path)
        print("format:", img.format)
        print("size:", img.size)
        print("mode:", img.mode)
        print("has exif:", bool(img.getexif()))


def convert_and_save_png(image_path: Path = DEFAULT_IMAGE_PATH) -> Path:
    """
    图片格式转换示例：JPEG -> PNG。

    Args:
        image_path (Path): 输入图片路径。

    Returns:
        Path: 输出 PNG 文件路径。

    逻辑说明：
        - Pillow 根据保存后缀自动选择编码器。
        - 这里不改变像素，只做格式转换。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_converted.png"

    with Image.open(image_path) as img:
        img.save(output_path)

    print("saved:", output_path)
    return output_path


def resize_thumbnail(
    image_path: Path = DEFAULT_IMAGE_PATH, max_size: tuple[int, int] = (320, 320)
) -> Path:
    """
    缩略图示例：按比例缩放到指定最大边界。

    Args:
        image_path (Path): 输入图片路径。
        max_size (tuple[int, int]): 缩略图最大宽高。

    Returns:
        Path: 输出缩略图路径。

    逻辑说明：
        - `thumbnail` 会原地修改图像对象，并保持宽高比。
        - 与 `resize` 不同，`thumbnail` 不会强行拉伸变形。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_thumbnail.jpg"

    with Image.open(image_path) as img:
        work = img.copy()
        # LANCZOS 适合高质量缩小
        work.thumbnail(max_size, Image.Resampling.LANCZOS)
        work.save(output_path, quality=90)

    print("saved:", output_path)
    return output_path


def center_crop_square(image_path: Path = DEFAULT_IMAGE_PATH, side: int = 400) -> Path:
    """
    居中裁剪正方形头像示例。

    Args:
        image_path (Path): 输入图片路径。
        side (int): 目标正方形边长。

    Returns:
        Path: 输出裁剪图片路径。

    逻辑说明：
        - 先根据短边裁出居中正方形区域。
        - 再缩放到固定尺寸，便于头像等场景统一规格。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_center_crop_square.jpg"

    with Image.open(image_path) as img:
        w, h = img.size
        short_side = min(w, h)
        left = (w - short_side) // 2
        top = (h - short_side) // 2
        right = left + short_side
        bottom = top + short_side

        # 先裁剪中心正方形区域
        cropped = img.crop((left, top, right, bottom))
        # 再统一到指定大小
        result = cropped.resize((side, side), Image.Resampling.LANCZOS)
        result.save(output_path, quality=92)

    print("saved:", output_path)
    return output_path


def rotate_with_expand(
    image_path: Path = DEFAULT_IMAGE_PATH, angle: float = 25
) -> Path:
    """
    旋转图片示例（保留完整画面）。

    Args:
        image_path (Path): 输入图片路径。
        angle (float): 旋转角度（逆时针）。

    Returns:
        Path: 输出旋转图路径。

    逻辑说明：
        - `expand=True` 表示自动扩展画布，避免旋转后内容被裁掉。
        - 对 JPEG 结果可设置 quality 控制体积和画质。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_rotate.jpg"

    with Image.open(image_path) as img:
        rotated = img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        rotated.save(output_path, quality=90)

    print("saved:", output_path)
    return output_path


def apply_filters(image_path: Path = DEFAULT_IMAGE_PATH) -> dict[str, Path]:
    """
    常见滤镜示例：模糊、锐化、边缘增强。

    Args:
        image_path (Path): 输入图片路径。

    Returns:
        dict[str, Path]: 各滤镜结果的输出路径字典。

    逻辑说明：
        - 使用 `ImageFilter` 提供的内置滤镜。
        - 同一张原图输出多个结果，方便对比效果。
    """
    out_dir = ensure_output_dir()
    outputs = {
        "blur": out_dir / "wechat_filter_blur.jpg",
        "sharpen": out_dir / "wechat_filter_sharpen.jpg",
        "edge_enhance": out_dir / "wechat_filter_edge_enhance.jpg",
    }

    with Image.open(image_path) as img:
        img.filter(ImageFilter.GaussianBlur(radius=2)).save(outputs["blur"], quality=90)
        img.filter(ImageFilter.SHARPEN).save(outputs["sharpen"], quality=90)
        img.filter(ImageFilter.EDGE_ENHANCE_MORE).save(
            outputs["edge_enhance"], quality=90
        )

    for path in outputs.values():
        print("saved:", path)
    return outputs


def adjust_brightness_contrast(image_path: Path = DEFAULT_IMAGE_PATH) -> Path:
    """
    图像增强示例：亮度 + 对比度调节。

    Args:
        image_path (Path): 输入图片路径。

    Returns:
        Path: 输出增强图路径。

    逻辑说明：
        - `ImageEnhance.Brightness` 调整亮度。
        - `ImageEnhance.Contrast` 调整对比度。
        - 先亮度后对比度，仅用于演示处理链式操作。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_enhanced.jpg"

    with Image.open(image_path) as img:
        brighter = ImageEnhance.Brightness(img).enhance(1.15)
        enhanced = ImageEnhance.Contrast(brighter).enhance(1.2)
        enhanced.save(output_path, quality=92)

    print("saved:", output_path)
    return output_path


def draw_text_and_rectangle(image_path: Path = DEFAULT_IMAGE_PATH) -> Path:
    """
    绘制图形和文字示例。

    Args:
        image_path (Path): 输入图片路径。

    Returns:
        Path: 输出绘制后图片路径。

    逻辑说明：
        - `ImageDraw.Draw` 可在图像上绘制矩形、线条、文字等。
        - 为避免系统字体依赖，这里使用默认字体 `draw.text`。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_draw.jpg"

    with Image.open(image_path) as img:
        work = img.copy()
        draw = ImageDraw.Draw(work)

        # 在左上角画一个框，用于标注演示
        draw.rectangle((20, 20, 260, 100), outline=(255, 80, 80), width=4)
        # 添加简单文字说明
        draw.text((30, 48), "Pillow Demo", fill=(255, 80, 80))

        work.save(output_path, quality=90)

    print("saved:", output_path)
    return output_path


def create_contact_sheet(image_path: Path = DEFAULT_IMAGE_PATH) -> Path:
    """
    拼图（contact sheet）示例：把多种处理效果拼成一张总览图。

    Args:
        image_path (Path): 输入图片路径。

    Returns:
        Path: 输出拼图路径。

    逻辑说明：
        - 先生成多个变体（原图、灰度、镜像、翻转）。
        - 每个小图统一尺寸后，按网格粘贴到一张大图上。
        - 该方式适合批量效果预览。
    """
    out_dir = ensure_output_dir()
    output_path = out_dir / "wechat_contact_sheet.jpg"

    with Image.open(image_path) as img:
        tile_size = (240, 240)
        variants = [
            img.copy(),
            ImageOps.grayscale(img).convert("RGB"),
            ImageOps.mirror(img),
            ImageOps.flip(img),
        ]

        # 统一每个 tile 尺寸，防止拼图时布局错位
        tiles = [v.resize(tile_size, Image.Resampling.LANCZOS) for v in variants]

        cols, rows = 2, 2
        sheet = Image.new(
            "RGB", (tile_size[0] * cols, tile_size[1] * rows), (245, 245, 245)
        )

        for idx, tile in enumerate(tiles):
            x = (idx % cols) * tile_size[0]
            y = (idx // cols) * tile_size[1]
            sheet.paste(tile, (x, y))

        sheet.save(output_path, quality=92)

    print("saved:", output_path)
    return output_path


def run_all_pillow_demos(image_path: Path = DEFAULT_IMAGE_PATH) -> None:
    """
    统一执行所有 Pillow 学习示例。

    Args:
        image_path (Path): 输入图片路径。

    Returns:
        None

    逻辑说明：
        - 入口函数，便于你一次性跑完全部例子。
        - 每一步会将结果保存到 `assets/output/`，可直接打开对比。
    """
    if not image_path.exists():
        raise FileNotFoundError(f"input image not found: {image_path}")

    show_image_info(image_path)
    convert_and_save_png(image_path)
    resize_thumbnail(image_path)
    center_crop_square(image_path)
    rotate_with_expand(image_path)
    apply_filters(image_path)
    adjust_brightness_contrast(image_path)
    draw_text_and_rectangle(image_path)
    create_contact_sheet(image_path)

    print("\nAll Pillow demos finished. Check:", OUTPUT_DIR)


if __name__ == "__main__":
    run_all_pillow_demos()
