from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math, string
import sys, os
from qzoneinfo.settings import BASE_DIR
from django.http.response import HttpResponse
from django.core.paginator import Paginator

# Create your views here.

def verify_code(request):
    code_path = os.path.join(BASE_DIR, 'static/images')
    _letter_cases = "abcdefghjkmnpqrstuvwxy"  # 小写字母，去除可能干扰的i，l，o，z
    _upper_cases = _letter_cases.upper()
    _numbers = ''.join(map(str, range(3, 10)))
    init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
    size = (100, 30)
    mode = "RGB"
    bg_color = (255, 255, 255)
    fg_color = (0, 0, 255)
    font_size = 18
    n_line = (1, 5),
    draw_points = True
    point_chance = 2
    line_color = (255, 0, 0)
    number = 4
    draw_line = True
    font_path = os.path.join(BASE_DIR, 'static/fonts/Arial.ttf')

    def gene_text():
        return ''.join(random.sample(init_chars, number))

    def gene_line(draw, width, height):
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([begin, end], fill = line_color)

    def gene_points(draw, width, height):
        chance = min(100, max(0, int(point_chance)))
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def gene_code(save_path, filename):
        width, height = size
        image = Image.new(mode, (width, height), bg_color)
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(image)
        text = gene_text()
        strs = ' %s ' % ' '.join(text)
        font_width, font_height = font.getsize(strs)
        draw.text(((width-font_width)/3, (height-font_height)/3), strs, font=font, fill=fg_color)
        if draw_line:
            gene_line(draw, width, height)
            gene_line(draw, width, height)
            gene_line(draw, width, height)
            gene_line(draw, width, height)
        if draw_points:
            gene_points(draw, width, height)

        params = [1 - float(random.randint(1, 2)) / 100,
                  0,
                  0,
                  0,
                  1 - float(random.randint(1, 10)) / 100,
                  float(random.randint(1, 2)) / 500,
                  0.001,
                  float(random.randint(1, 2)) / 500
                  ]
        image = image.transform(size, Image.PERSPECTIVE, params)
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        image.save('%s/%s.png' % (save_path, filename))
        print('savepath:   '+save_path)
        return text

    vcode = gene_code(code_path, 'verifycode')
    print(vcode)
    request.session['vcode'] = vcode

    return HttpResponse('ok')

def page_to_page(request, page, friends):
    p = Paginator(friends, page)  # 分页，3篇文章一页
    if p.num_pages <= 1:  # 如果文章不足一页
        friend_list = friends  # 直接返回所有文章
        data = ''  # 不需要分页按钮
    else:
        page = int(request.GET.get('page', 1))  # 获取请求的文章页码，默认为第一页
        friend_list = p.page(page)  # 返回指定页码的页面
        left = []  # 当前页左边连续的页码号，初始值为空
        right = []  # 当前页右边连续的页码号，初始值为空
        left_has_more = False  # 标示第 1 页页码后是否需要显示省略号
        right_has_more = False  # 标示最后一页页码前是否需要显示省略号
        first = False  # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        last = False  # 标示是否需要显示最后一页的页码号。
        total_pages = p.num_pages
        page_range = p.page_range
        if page == 1:  # 如果请求第1页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            print(total_pages)
            if right[-1] < total_pages - 1:  # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
                # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
                right_has_more = True
            if right[-1] < total_pages:  # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                # 所以需要显示最后一页的页码号，通过 last 来指示
                last = True
        elif page == total_pages:  # 如果请求最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            if left[0] > 2:
                left_has_more = True  # 如果最左边的号码比2还要大，说明其与第一页之间还有其他页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 1:  # 如果最左边的页码比1要大，则要显示第一页，否则第一页已经被包含在其中
                first = True
        else:  # 如果请求的页码既不是第一页也不是最后一页
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]  # 获取左边连续号码页
            right = page_range[page:page + 2]  # 获取右边连续号码页
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        data = {  # 将数据包含在data字典中
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
            'total_pages': total_pages,
            'page': page
        }
    return data, friend_list
