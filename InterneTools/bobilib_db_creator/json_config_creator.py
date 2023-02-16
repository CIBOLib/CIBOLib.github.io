import json

if __name__ == "__main__": 

    collection_home = input("Path to collection (.../collection): ")
    htmls_home = input("Path for htmls (.../BOBILib.github.io/htmls): ")
    layout_home = input("complete Path to default.html (.../BOBILib.github.io/_layouts/default.html): ")
    css_home = input("complete Path to main.css (.../BOBILib.github.io/css/main.css): ")
    ask_compress=input("Do you want to compress the collection subdirectories? ['Yes' or 'yes' or 'y'| no=anything else] ")
    compress = False
    archives_home=""
    if ask_compress=="Yes" or ask_compress=="yes" or ask_compress=="y":
        compress=True
        while len(archives_home)==0:
            archives_home = input("Path for archives (.../archives): ")
    
    config_dict={"collection_home":collection_home, "htmls_home":htmls_home, 
        "layout_home":layout_home,"css_home":css_home,"archives_home":archives_home,
        "compress":compress}

    config_file = open("./config.json", "w")
    json.dump(config_dict, config_file)
    config_file.close()

    