def remove_quotes(string):
  string = string.strip()
  start = 0
  adjuster = 1
  end = len(string) - adjuster
  if string[0] == "\'" or string[0] == "\"":
    start = 1
  
  if string[end] == "\'"  or string[end] == "\"":
    adjuster = 2
  return string[start: end].strip()

def format_to_object(dataList):
    new_object = {}
    for x in dataList:
      formatted_key = remove_quotes(x.split(": ")[0].strip())
      # formatted_key = formatted_key[1:len(formatted_key)-1]
      new_object[formatted_key] = x.split(": ")[1]
    
    for x in new_object:
      try:
        if 'seeking' in x:
          if new_object[x].lower() == 'true':
            new_object[x] = True
          elif new_object[x].lower() == 'false':
            new_object[x] = False
        new_object[x] = int(new_object[x])
      except:
        print()
    return new_object


def format_genre_to_list(thisString):
	new_list = thisString.split(", ")

	for x in new_list:
		x = x.strip()
	return new_list

def add_venue_data(outerObject, model, innerObject, idName):
	for x in outerObject[innerObject]:
		data = model.query.get(x[idName])
		print(data)
		x["venue_name"] = data.name
		x["venue_image_link"] = data.image_link
		 
