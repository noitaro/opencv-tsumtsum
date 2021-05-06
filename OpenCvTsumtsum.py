import datetime
import os
import cv2
import numpy
import itertools

COLOR_THRESHOLD = 10


def routeSearch(imgArray, save=False):
    open_cv_image = numpy.array(imgArray)
    # Convert RGB to BGR
    img = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

    circles = GetHoughCircles(img)
    if circles is None: return []
    averaging = GetAveraging(img, circles)
    routing = GetRouting(averaging)

    if save:
        # 描画
        for item in averaging:
            cv2.circle(img, (item['x'], item['y']), item['radius'], (item['blue'], item['green'], item['red']), thickness=-1)
            cv2.putText(img, str(item['group']), (item['x']-10, item['y']+12), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), thickness=2)
            cv2.putText(img, str(item['index']), (item['x']+10, item['y']+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)
        for item in routing:
            cv2.arrowedLine(img, (averaging[item[0]]['x'], averaging[item[0]]['y']), (
                averaging[item[1]]['x'], averaging[item[1]]['y']), (0, 255, 0), thickness=4)

        fileName = 'tsumtsum/screenshot_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'

        # 保存先のフォルダを取得
        dirname = os.path.dirname(fileName)

        # フォルダが指定してあれば、作成
        if len(dirname) != 0: os.makedirs(dirname, exist_ok=True)

        # キャプチャ画像保存
        cv2.imwrite(fileName, img)

    route = []
    for index, item in enumerate(routing):
        if index <= 0:
            # 初回
            route.append((round(averaging[item[0]]['x']), round(averaging[item[0]]['y'])))
        route.append((round(averaging[item[1]]['x']), round(averaging[item[1]]['y'])))
    print(route)

    return route


def GetHoughCircles(img):
    cimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, 1, 25, param1=100, param2=25, minRadius=25, maxRadius=45)
    if circles is not None:
        circles = numpy.uint16(numpy.around(circles))
    return circles


def GetAveraging(img, circles):
    average = []

    index = 0
    for i in circles[0, :]:
        # img[top : bottom, left : right]
        imgcrop = img[i[1]-5: i[1]+5, i[0]-5: i[0]+5]
        # imgblur = cv2.blur(imgcrop, (15, 15))

        b = round(imgcrop.T[0].flatten().max() * 0.1) * 10
        g = round(imgcrop.T[1].flatten().max() * 0.1) * 10
        r = round(imgcrop.T[2].flatten().max() * 0.1) * 10

        average.append({'index': index, 'blue': b, 'green': g, 'red': r, 'x': i[0], 'y': i[1], 'radius': i[2], 'group': -1})
        index = index + 1

    SetGrouping(average)

    return average


def SetGrouping(averaging):

    group = []
    for average in averaging:
        isOK = False

        # 初回
        if len(group) <= 0:
            average['group'] = len(group)
            group.append({'group': average['group'], 'blue': average['blue'], 'green': average['green'], 'red': average['red']})

        for index in list(range(len(group))):
            blue = round(numpy.mean([i['blue'] for i in averaging if i['group'] == index]))
            green = round(numpy.mean([i['green'] for i in averaging if i['group'] == index]))
            red = round(numpy.mean([i['red'] for i in averaging if i['group'] == index]))

            if blue - COLOR_THRESHOLD <= average['blue'] and average['blue'] <= blue + COLOR_THRESHOLD and \
               green - COLOR_THRESHOLD <= average['green'] and average['green'] <= green + COLOR_THRESHOLD and \
               red - COLOR_THRESHOLD <= average['red'] and average['red'] <= red + COLOR_THRESHOLD:

                isOK = True
                average['group'] = index
                break

        if not isOK:
            average['group'] = len(group)
            group.append({'group': average['group'], 'blue': average['blue'], 'green': average['green'], 'red': average['red']})

    return


def GetRouting(averaging):
    target = []

    for index in list(range(max([i['group'] for i in averaging]))):
        items = list(filter(lambda x: x['group'] == index, averaging))
        route = RouteSearch1(items)
        if len(target) < len(route):
            target = list(route)

    return target


def RouteSearch1(items):
    fragment = []

    for item in items:
        route = RouteSearch2(item, list(filter(lambda x: x != item, items)))
        fragment.append(route)

    fragment = list(itertools.chain.from_iterable(fragment))  # 平坦化
    # print(fragment)

    target = []
    for item in fragment:
        route = RouteSearch3([item], list(
            filter(lambda x: x != item, fragment)))
        if len(target) < len(route):
            target = list(route)

    return target


def RouteSearch2(target, items):
    fragment = []

    for item in items:

        if target['x'] <= item['x']:
            ax = target['x']
            bx = item['x']
        else:
            ax = item['x']
            bx = target['x']

        if target['y'] <= item['y']:
            ay = target['y']
            by = item['y']
        else:
            ay = item['y']
            by = target['y']

        a = numpy.array([ax, ay])
        b = numpy.array([bx, by])
        norm = numpy.linalg.norm(b - a)
        if norm < 70:
            fragment.append([target['index'], item['index']])

    return fragment


def RouteSearch3(targets, items):
    route = list(targets)

    target = targets[-1]
    filtering = set(list(itertools.chain.from_iterable(targets)))
    for item in list(filter(lambda x: x[0] == target[1] and all([i != x[1] for i in filtering]), items)):
        routed = list(targets)
        routed.append(item)
        search = RouteSearch3(routed, list(filter(lambda x: x != item, items)))
        if len(route) < len(search):
            route = list(search)

    return route
