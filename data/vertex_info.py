import re
import json
import math
from svgpathtools import parse_path
from xml.dom import minidom
import numpy as np
import cv2
def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def svg_path_to_json(svg_path_strings, merge_distance=2.5):
    vertex_location = []
    connections = []
    for svg_path_string in svg_path_strings:
        path_data = parse_path(svg_path_string)
        path_data = path_data.d().split(" ")
        # Group adjacent elements into tuple pairs
        path_data = [(path_data[i], path_data[i+1]) for i in range(0, len(path_data), 2)]
        
        if len(path_data) < 200:
            continue
        print(len(path_data))
        for command, parameters in path_data:

            if command == 'M':
                x, y = map(float, parameters.split(","))
                vertex_location.append([x, y])
                connections.append([len(vertex_location) - 1])
            elif command == 'L':
                x, y = map(float, parameters.split(","))
                current_point = [x, y]
                # Check for merging with previous points
                merged = False
                # vertex_ind = len(vertex_location) - 1
                # for i in range(len(vertex_location)-1, 0, -1):
                #     last_point = vertex_location[i]
                #     if euclidean_distance(last_point, current_point) <= merge_distance:
                #         # Merge the current point with the last point
                #         vertex_location[i] = [(last_point[0]+current_point[0])/2, (last_point[1]+current_point[1])/2]
                #         vertex_ind = i
                #         merged = True
                #         break
                if not merged:
                    vertex_location.append(current_point)
                    connections.append([len(vertex_location) - 2, len(vertex_location) - 1])
                

    json_data = {
        "vertex location": vertex_location,
        "connection": connections,
        "original index": [i for i in range(len(vertex_location))],

    }
    print("Output Vertices", len(vertex_location))
    print("Output connections", len(connections))

    return json_data

def draw_cv2(data, fname):
    canvas2 = np.zeros((720,720,1)) + 255

    vertices = np.round(np.array(data["vertex location"])).astype("int")

    print(vertices[:10])
    for arr in (data["connection"]):
        if len(arr)!=2:
            continue
        ind1, ind2 = arr[0], arr[1]
        # print(ind1, ind2)
        # print((vertices[ind1][0], vertices[ind1][1]), (vertices[ind2][0], vertices[ind2][1]))
        cv2.line(canvas2, (vertices[ind1][0], vertices[ind1][1]), (vertices[ind2][0], vertices[ind2][1]), [0, 0, 0], 2)
    
    cv2.imwrite(fname, canvas2)

import json
index=1
for i in range(1,13):
    # Example SVG path string
    svg_contents = ""
    with open(f"./cat_svg/Image_000{i}.svg", 'r') as f:
        svg_contents = f.read()

    print("Content", len(svg_contents))
    svg_dom = minidom.parseString(svg_contents)
    path_strings = [path.getAttribute('d') for path in svg_dom.getElementsByTagName('path')]

    json_data = svg_path_to_json(path_strings)
    draw_cv2(json_data, f'./cat_res/img_{i}.png')
    # filename = f'./cat_res/img_{index}.json'
    filename = f'./anime/all/labels/cat/Line{index:04}.json'

    index+=1
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
