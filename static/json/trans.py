import json

def tran_json_tree(jsondatas):
    ret = []
    o = {}
    def add(arr, data):
        obj = {
            'id': data['id'],
            'upid': data['upid'],
            'children': [],
            'cname': data['cname'],
            'ename': data['ename'],
            'pinyin': data['pinyin'],
            'level': data['level']
        }
        o[data['id']] = obj
        arr.append(obj)
    for jsondata in jsondatas:
        if jsondata['upid'] in o:
            add(o[jsondata['upid']]['children'], jsondata)
        else:
            add(ret, jsondata)
    return ret

def tran_json_search_father(jsondatas):
    level0 = []
    level1 = []
    level2 = []
    level3 = {}
    for jsondata in jsondatas:
        if jsondata['level'] == '3':
            level3[jsondata['id']] = [jsondata['upid']]
        if jsondata['level'] == '2':
            level3[jsondata['id']].append(jsondata['upid'])
        if jsondata['level'] == '1':
            level3[jsondata['id']].append(jsondata['upid'])
    return level3
def tran_json_dict(jsondatas):
    res_dict = {}
    for jsondata in jsondatas:
        res_dict[jsondata['id']] = {
            'upid': jsondata['upid'],
            'cname': jsondata['cname'],
            'pinyin': jsondata['pinyin'],
            'level': jsondata['level'],
        }
    return res_dict

def tran_json_childandfa(jsondatas):
    res = {}
    for i in jsondatas:
        if jsondatas[i]['level'] == '3':
            res[i] = {}
            res[i]['cname'] = jsondatas[i]['cname']
            res[i]['parent'] = [{
                'cname': jsondatas[jsondatas[i]['upid']]['cname'],
                'id': jsondatas[i]['upid']
            },
            {
                'cname': jsondatas[jsondatas[jsondatas[i]['upid']]['upid']]['cname'],
                'id: ': jsondatas[jsondatas[i]['upid']]['upid']
            }]
    return res

with open('./sql_areas.json') as f:
    data = json.load(f)
jsondatas = tran_json_dict(data)
datas = tran_json_childandfa(jsondatas)
print(datas)


with open('./sql_json_childfa.json', 'a') as f:
    json.dump(datas, f, ensure_ascii=False)
