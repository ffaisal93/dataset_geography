from wikidata.client import Client
import json
import csv
from collections import defaultdict
import numpy as np
import pickle

with open('country_dict.json') as inp:
    lines = inp.read()
country_dict = json.loads(lines)
#except:
#    country_dict = {}
#try:
with open('country_dict_r.json') as inp:
    lines = inp.read()
country_dict_r = json.loads(lines)


c2code = {}
code2c = {}
with open("data/wikipedia-iso-country-codes.csv") as f:
    file= csv.DictReader(f, delimiter=',')
    for line in file:
        c2code[line['English short name lower case']] = line['Alpha-3 code']  
        code2c[line['Alpha-3 code']] = line['English short name lower case']

def get_name(ent):
    if str(ent).count("\'") == 2:
        return str(ent)[str(ent).find("\'")+1:str(ent).rfind("\'")]
    elif str(ent).count('\"') == 2:
        return str(ent)[str(ent).find("\"")+1:str(ent).rfind("\"")]

#countries_to_check = ['Canada','Lithuania','Austria','German Confederation','Poland','Czech Republic']
countries_to_check = []

for LANG in ['bengali','arabic', 'english', 'finnish', 'indonesian', 'japanese', 'korean', 'russian', 'swahili', 'telugu', 'thai']:
    with open(f"../data/entities/tydiqa/tydiqa-dev-{LANG}.pickle", 'rb') as inp:
        lines = pickle.load(inp)

    client = Client()

    json_name = 'tydiqa_data/all_d.json'
    with open(json_name) as inp:
        jsonstr = inp.read()
    d = json.loads(jsonstr)
    #d = {}

    lang_entities = []
    countc = 0
    for k in lines:
        #print(k)
        try:
            l = k[0]['id']
        except:
            continue
        countc += 1
        #l = l.strip().split('\t')[0]
        lang_entities.append(l)
        to_check = False
        if l in d:
            codes_to_check = [country_dict_r[ccc] for ccc in countries_to_check]
            if 'country' in d[l]:
                if d[l]['country'] in codes_to_check:
                    to_check=True
            if 'citizen' in d[l]:
                if d[l]['citizen'] in codes_to_check:
                    to_check=True
            if 'born' in d[l]:
                if d[l]['born'] in codes_to_check:
                    to_check=True
            if 'died' in d[l]:
                if d[l]['died'] in codes_to_check:
                    to_check=True
        #for key in entity:
        #    print(str(key))
        if (l not in d) or to_check:
            try:
                entity = client.get(l, load=True)
            except:
                lang_entities.remove(l)
                continue
            #print(entity)
            name = get_name(entity)
            print(name)
            d[l] = {}
            d[l]['name'] = name

            for key in entity.keys():
                try:
                    if key.id == 'P31':
                        #print(f'instance of: {entity[key].id}')
                        #print(key.id, entity[key])
                        if entity[key].id == 'Q5':
                            #print('\thuman')
                            d[l]['instance'] = 'human'
                        elif entity[key].id == 'Q515':
                            #print('\tcity')
                            d[l]['instance'] = 'city'
                        elif entity[key].id == 'Q6256':
                            #print('\tcountry')
                            d[l]['instance'] = 'country'
                    if key.id in 'P27,P19,P20,P17,P1376,P625,P69,P276,P495,P159'.split(','):
                        #print(key.id, entity[key])
                        if key.id == 'P17':
                            #print(f'\tcountry: {entity[key].id}')
                            d[l]['country'] = entity[key].id
                        elif key.id == 'P20':
                            #print(f'\tdied in: {entity[key].id}')
                            d[l]['died'] = entity[key].id
                        elif key.id == 'P19':
                            #print(f'\tborn in: {entity[key].id}')
                            d[l]['born'] = entity[key].id
                        elif key.id == 'P27':
                            #print(f'\tcitizen of: {entity[key].id}')
                            d[l]['citizen'] = entity[key].id
                        elif key.id == 'P69':
                            #print(f'\teducated at: {entity[key].id}')
                            d[l]['educated'] = entity[key].id
                        elif key.id == 'P276':
                            #print(f'\tlocated at: {entity[key].id}')
                            d[l]['located'] = entity[key].id
                        elif key.id == 'P159':
                            #print(f'\theadquartered at: {entity[key].id}')
                            d[l]['headquartered'] = entity[key].id
                        elif key.id == 'P495':
                            #print(f'\toriginated from: {entity[key].id}')
                            d[l]['from'] = entity[key].id
                        elif key.id == 'P1376':
                            #print(f'\tcapital of: {entity[key].id}')
                            d[l]['capital'] = entity[key].id
                        elif key.id == 'P625':
                            #print(f'\tcoordinates: {entity[key]}')
                            temp = str(entity[key]).split('(')[1]
                            latitude = float(temp.split(',')[0])
                            longtidute = float(temp.split(',')[1])
                            d[l]['coordinates'] = (latitude,longtidute)
                except:
                    pass
        if countc == 100:
            countc = 0
            jsonString = json.dumps(d)
            json_name = f"tydiqa_data/all_d.json"
            with open(json_name, 'w') as op:
                op.write(jsonString)


    new_d = {}
    for l in lang_entities:
        try:
            new_d[l] = d[l]
        except:
            continue

    jsonString = json.dumps(d)
    json_name = f"tydiqa_data/all_d.json"
    with open(json_name, 'w') as op:
        op.write(jsonString)

    jsonString = json.dumps(new_d)
    json_name = f"tydiqa_data/{LANG}_d.json"
    with open(json_name, 'w') as op:
        op.write(jsonString)

    d = new_d

    print("************************")
    #except:
    #    country_dict_r = {}

    with open('place2country.json') as inp:
        lines = inp.read()
    place2country = json.loads(lines)
    #place2country = {}

    with open('id2geo.json') as inp:
        lines = inp.read()
    id2geo = json.loads(lines)
    #id2geo = {}

    count = 0
    count2 = 0
    for key in lang_entities:
        count2 += 1
        if key in id2geo:
            to_continue = True
            if 'country' in id2geo[key]:
                if id2geo[key]['country'] in countries_to_check:
                    to_continue=False
            if 'citizen' in id2geo[key]:
                if id2geo[key]['citizen'] in countries_to_check:
                    to_continue=False
            if 'born' in id2geo[key]:
                if id2geo[key]['born'] in countries_to_check:
                    to_continue=False
            if 'died' in id2geo[key]:
                if id2geo[key]['died'] in countries_to_check:
                    to_continue=False
            if to_continue:
                continue
        if 'country' in d[key]:
            print('>found country')
            if d[key]['country'] in country_dict:
                print(f"{key}\t{d[key]['name']}\tcountry:{country_dict[d[key]['country']]}")
                if key not in id2geo:
                    id2geo[key] = {}
                id2geo[key]['name'] = d[key]['name']
                id2geo[key]['country'] = country_dict[d[key]['country']]
            else:
                country = client.get(d[key]['country'], load=True)
                country_name = get_name(country)
                print(f"{key}\t{d[key]['name']}\tcountry:{country_name}")
                country_dict[country.id] = country_name
                country_dict_r[country_name] = country.id
                count += 1
                if key not in id2geo:
                    id2geo[key] = {}
                id2geo[key]['name'] = d[key]['name']
                id2geo[key]['country'] = country_name

        if 'citizen' in d[key]:
            print('>found citizen')
            if d[key]['citizen'] in country_dict:
                print(f"{key}\t{d[key]['name']}\tcitizen:{country_dict[d[key]['citizen']]}")    
                if key not in id2geo:
                    id2geo[key] = {}
                id2geo[key]['name'] = d[key]['name']
                id2geo[key]['citizen'] = country_dict[d[key]['citizen']]
            else:
                place = client.get(d[key]['citizen'], load=True)
                country_name = get_name(place)
                print(f"{key}\t{d[key]['name']}\tcitizen:{country_name}")
                country_dict[place.id] = country_name
                country_dict_r[country_name] = place.id
                count += 1
                if key not in id2geo:
                    id2geo[key] = {}
                id2geo[key]['name'] = d[key]['name']
                id2geo[key]['citizen'] = country_name


        if 'born' in d[key]:
            print('>found born')
            if d[key]['born'] in place2country:
                print(f"{key}\t{d[key]['name']}\tborn:{place2country[d[key]['born']]['country']}")
                if key not in id2geo:
                    id2geo[key] = {}
                id2geo[key]['name'] = d[key]['name']
                id2geo[key]['born'] = place2country[d[key]['born']]['country']
            else:
                if d[key]['born']=='Q2042400':
                    print('')
                place = client.get(d[key]['born'], load=True)
                for key2 in place.keys():
                    if key2.id == 'P17':
                        try:
                            countryid = place[key2].id
                        except:
                            print(key2, key, d[key], place)
                            continue
                        if countryid in country_dict:
                            print(f"{key}\t{d[key]['name']}\tborn:{country_dict[countryid]}")
                            if key not in id2geo:
                                id2geo[key] = {}
                            id2geo[key]['name'] = d[key]['name']
                            id2geo[key]['born'] = country_dict[countryid]
                            place2country[d[key]['born']] = {}
                            place2country[d[key]['born']]['name'] = get_name(place)
                            place2country[d[key]['born']]['country'] = country_dict[countryid]
                        else:
                            country = client.get(countryid, load=True)
                            country_name = get_name(country)
                            print(f"{key}\t{d[key]['name']}\tborn:{country_name}")
                            country_dict[country.id] = country_name
                            country_dict_r[country_name] = country.id
                            place2country[d[key]['born']] = {}
                            place2country[d[key]['born']]['name'] = get_name(place)
                            place2country[d[key]['born']]['country'] = country_name
                            count += 1
                            if key not in id2geo:
                                id2geo[key] = {}
                            id2geo[key]['name'] = d[key]['name']
                            id2geo[key]['born'] = country_name

        if 'died' in d[key]:
            print('>found died')
            if d[key]['died'] in place2country:
                print(f"{key}\t{d[key]['name']}\tdied:{place2country[d[key]['died']]['country']}")
                if key not in id2geo:
                    id2geo[key] = {}
                id2geo[key]['name'] = d[key]['name']
                id2geo[key]['died'] = place2country[d[key]['died']]['country']
            else:
                place = client.get(d[key]['died'], load=True)
                for key2 in place.keys():
                    if key2.id == 'P17':
                        try:
                            countryid = place[key2].id
                        except:
                            print(key2, key, d[key], place)
                            continue
                        if countryid in country_dict:
                            print(f"{key}\t{d[key]['name']}\tdied:{country_dict[countryid]}")
                            if key not in id2geo:
                                id2geo[key] = {}
                            id2geo[key]['name'] = d[key]['name']
                            id2geo[key]['died'] = country_dict[countryid]
                            place2country[d[key]['died']] = {}
                            place2country[d[key]['died']]['name'] = get_name(place)
                            place2country[d[key]['died']]['country'] = country_dict[countryid]
                        else:
                            country = client.get(countryid, load=True)
                            country_name = get_name(country)
                            print(f"{key}\t{d[key]['name']}\tdied:{country_name}")
                            country_dict[country.id] = country_name
                            country_dict_r[country_name] = country.id
                            place2country[d[key]['died']] = {}
                            place2country[d[key]['died']]['name'] = get_name(place)
                            place2country[d[key]['died']]['country'] = country_name
                            count += 1
                            if key not in id2geo:
                                id2geo[key] = {}
                            id2geo[key]['name'] = d[key]['name']
                            id2geo[key]['died'] = country_name
        #print(count)
        if count == 50:
            jsonString = json.dumps(country_dict)
            with open("country_dict.json", 'w') as op:
                op.write(jsonString)

            jsonString = json.dumps(country_dict_r)
            with open("country_dict_r.json", 'w') as op:
                op.write(jsonString)

            jsonString = json.dumps(id2geo)
            with open("id2geo.json", 'w') as op:
                op.write(jsonString)

            jsonString = json.dumps(place2country)
            with open("place2country.json", 'w') as op:
                op.write(jsonString)
            count = 0
        if count2 == 50:
            jsonString = json.dumps(id2geo)
            with open("id2geo.json", 'w') as op:
                op.write(jsonString)
            count2 = 0



    jsonString = json.dumps(country_dict)
    with open("country_dict.json", 'w') as op:
        op.write(jsonString)

    jsonString = json.dumps(country_dict_r)
    with open("country_dict_r.json", 'w') as op:
        op.write(jsonString)

    jsonString = json.dumps(id2geo)
    with open("id2geo.json", 'w') as op:
        op.write(jsonString)

    jsonString = json.dumps(place2country)
    with open("place2country.json", 'w') as op:
        op.write(jsonString)


    from urllib.request import urlopen
    import json
    #with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    #    counties = json.load(response)

    #print(counties["features"][0])

    import pandas as pd

    # import plotly.express as px
    # import plotly.graph_objects as go

    country_list = list(c2code.keys())
    iso_list = [c2code[c] for c in country_list]
    print(len(country_list))
    print(country_list)
    print(iso_list)

    mapping = {}
    mapping['United States of America'] = 'United States'
    mapping["People's Republic of China"] = 'China'
    mapping["The Bahamas"] = 'Bahamas'
    mapping["Ivory Coast"] = "Côte d'Ivoire"
    mapping["Democratic Republic of the Congo"] = "D.R. Congo"
    mapping["Republic of the Congo"] = 'Congo'
    mapping["Dutch East Indies"] = 'Netherlands Antilles'
    mapping["Russian Republic"] = 'Russian Federation'
    mapping["The Gambia"] = 'Gambia'
    mapping["England"] = 'United Kingdom'
    mapping["Scotland"] = 'United Kingdom'
    mapping["Wales"] = 'United Kingdom'
    mapping["East Timor"] = 'Timor-Leste'
    mapping["North Macedonia"] = 'Macedonia'
    mapping["People's Republic of Angola"] = 'Angola'
    mapping["State of Palestine"] = 'Palestine'
    mapping["Federated States of Micronesia"] = 'Micronesia'
    mapping["Democratic Republic of Georgia"] = 'Georgia'
    mapping["Great Britain"] = 'United Kingdom'
    mapping["United Kingdom of Great Britain and Ireland"] = 'United Kingdom'
    mapping["Russia"] = 'Russian Federation'
    mapping["Laos"] = "Lao People's Democratic Republic"
    mapping["São Tomé and Príncipe"] = 'Sao Tome and Principe'
    mapping["Mongolian People's Republic"] = 'Mongolia'
    mapping["Sahrawi Arab Democratic Republic"] = 'Western Sahara'
    mapping["Serbia and Montenegro"] = 'Serbia'
    mapping["Somaliland"] = 'Somalia'
    mapping["Palestinian territories"] = 'Palestine'
    mapping["Northern Ireland"] = 'United Kingdom'
    mapping["Vatican City"] = 'Holy See'
    mapping["Czech REpublic"] = 'Czech Republic'
    mapping["AustriA"] = 'Austria'
    mapping["LIthuania"] = 'Lithuania'
    mapping[""] = ''
    mapping[""] = ''


    for key in country_dict_r:
        if key in country_list:
            print("found!", key)
            if key in c2code:
                print(f"\talso found ISO code: {c2code[key]}")
            else:
                print(f"\tdid not find ISO code: {key}")
        elif key in mapping:
            if mapping[key] in country_list:
                print("found!", mapping[key])
                if mapping[key] in c2code:
                    print(f"\talso found ISO code (map): {c2code[mapping[key]]}")
                else:
                    print(f"\tdid not find ISO code (map): {mapping[key]}")
        else:
            print("not!", key)

    dataset_counts = defaultdict(lambda:0)
    for key in lang_entities:
        if key in id2geo:
            name = id2geo[key]['name']
            if 'country' in id2geo[key] or 'citizen' in id2geo[key]:
                if 'country' in id2geo[key]:
                    country = id2geo[key]['country']
                else:
                    country = id2geo[key]['citizen']
                #print(country)
                if country in mapping:
                    country = mapping[country]
                if country in c2code:
                    code = c2code[country]
                    dataset_counts[code] += 1
            if 'born' in id2geo[key]:
                #print("BORN: ", id2geo[key]['born'])
                born = id2geo[key]['born']
                if born in mapping:
                    born = mapping[born]
                if born in c2code:
                    code = c2code[born]
                    dataset_counts[code] += 1
            if 'died' in id2geo[key]:
                #print("DIED: ", id2geo[key]['died'])
                died = id2geo[key]['died']
                if died in mapping:
                    died = mapping[died]
                if died in c2code:
                    code = c2code[died]
                    dataset_counts[code] += 1

    codes = list(code2c.keys())
    #print(codes)
    #logcounts = [np.log10(dataset_counts[c]) for c in codes]
    logcounts = []
    for c in codes:
        if dataset_counts[c]>0:
            logcounts.append(np.log10(dataset_counts[c]))
        else:
            logcounts.append(0)
    counts = [dataset_counts[c] for c in codes]
    sqrtcounts = np.sqrt(counts)
    #print(counts)
    names = [code2c[c] for c in codes]
    #print(names)
    texts = [f"{names[i]}<br>#entities: {counts[i]}" for i in range(len(codes))]

    df = pd.DataFrame({'iso_alpha': codes, 'country':names, 'counts':counts, 'log_counts':logcounts, 'text':texts, 'sqrt_counts':sqrtcounts})
    df.to_csv(f'tydiqa_count_csvs/tydiqa-{LANG}.csv')
    '''
    #fig = px.choropleth(df, 
    fig = go.Figure(data=go.Choropleth(
            locations=df["iso_alpha"],
            z=df["log_counts"], # lifeExp is a column of gapminder
            text=df["text"], # column to add to hover information
            #colorscale="Viridis",
            colorscale="Reds",
            marker_line_color='black',
            marker_line_width=0.5,
            colorbar_title = 'log(#entities)',
            ))
    fig.update_layout(title_text=f'Geographic Coverage: TREx-{LANG}', 
        geo=dict(
        showframe=True,
        showcoastlines=True,
        projection_type='natural earth'
    ))
    fig.write_image(f"plots/TREx-{LANG}.png")
    fig.show()
    '''



#================================================
    # fig = go.Figure(data=go.Scattergeo(
    #         locations=df["iso_alpha"],
    #         #size=df["log_counts"], # lifeExp is a column of gapminder
    #         text=df["text"], # column to add to hover information
    #         #colorscale="Viridis",
    #         mode = 'markers',
    #         marker_color = df['log_counts'],

    #         marker_size = df["log_counts"],
    #         #marker_sizemin = 6,
    #         marker_colorscale="Bluered",
    #         marker_sizeref = 0.08,
    #         #marker_line_color='black',
    #         #marker_line_width=0.5,
    #         marker_colorbar_title = 'log(#entities)',
    #         marker_colorbar_ticktext = [0,10,100,1000],
    #         ))
    # fig.update_layout(title_text=f'Geographic Coverage: tydiqa-{LANG}', 
    #     geo=dict(
    #     showframe=True,
    #     showcoastlines=True,
    #     showcountries=True,
    #     projection_type='natural earth'
    # ))
    # fig.write_image(f"plots/tydiqa-{LANG}.scatter.png")
    # fig.show()
#=================================================    

