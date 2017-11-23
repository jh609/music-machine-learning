from load_songs import *
from sklearn.decomposition import TruncatedSVD
import sys
import glob
import scipy.stats as stats
from collections import OrderedDict
from bokeh.plotting import *
from bokeh.models import *
from bokeh.io import *
from sklearn.manifold import TSNE

#This python script will take pre-made python dictionaries with feature information about an artists songs, and do some clustering and data visualisation, using bokeh to create html code for interactive plots.

#A note on data structures:
#When I load in songs and extract features in the other script, the data is stored in a nested dictinoary structure
#I'm using a nested dictionary, so my top level dictionary has keys which are song names, and values which are dictionaries of data.
#The next level, each song has a dictionary where keys are the feature names (e.g. spectral centroid, rms, ...), and values are the values associated with them. this makes it easy to access any song, and any feature.

#load in all data saved from the feature extraction, *.pkl. Python script requres path as an argument.
path=sys.argv[1]
all_data=glob.glob(path+'/*.pkl')

#Not needed at the moment, but in the future I will...
all_features=[]
all_artists=[]
all_songnames=[]
#Initiate figure and pick some colours
from bokeh.palettes import Category20_20 as palette

colors = itertools.cycle(palette)
output_file("plot_cluster.html", title="Song clustering")
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset"
p = figure(title="Song Clustering", tools=[TOOLS],plot_width=1300,plot_height=700)

#As i did feature extraction on each artist seperately, loop through them. Create lists of song names and features
for artist in all_data:
    data=load_obj(artist.replace('.pkl',''))
    print('loading {0}'.format(artist))
    songname=[] #will be a list of song names
    songfeat=[] #will be a list of dictionaries containing the song feature data
    artists=[] #will be a list of artists, as I load them artist at a time should be straightforward.
    
    artist_trimmed=artist.replace('_data.pkl','').replace('all_','').replace(path,'')
    for song in data: #data is a dictionary, keys are song names
        songfeat.append(data[song]) #data corresponding to each dictionary key is another dictionary with 25 features and labels
        songname.append(song.replace('artist_trimmed','').replace('.mp3','').replace('.wav','').replace('.wma','').replace('.m4a','')) #some songs have artist names at the beginning, remove file format endings also for clarity.
        artists.append(artist_trimmed)

    features=[] #will be all our raw feature data
    feature_names=[] #will be all our feature names
    feature_names.append(list(songfeat[0].keys()))
    for i in range(len(songfeat)):
        features.append(list(songfeat[i].values())) #take the songfeat dictionary and grab only the values (keys are just text labels for each feature)

    #create master lists of features and genres for the machine learning later - not used in this script yet.
    all_features+=features
    all_artists+=artists
    all_songnames+=songname
    # Here we do singular vector decomposition (SVD) or t distributed stocastic neighbor embedding (t-SNE). Basically we have 29 dimensions in our data set (29 features), and to visualise it we would rather have 2 dimensions. SVDs linearly combine higher dimensions down to how ever many you choose based on which ones it finds best distinguish the data.
    '''
    #if we want each artist plotted separately, do it here:
    svd = TruncatedSVD(n_components=2, n_iter=7, random_state=42) #initiate SVD
    reduced_data = svd.fit_transform(features) #Reduce data to 2 dimensions.
    reduced_data = TSNE(n_components=2, learning_rate=int(sys.argv[2])).fit_transform(features)
    plot_data=OrderedDict(x=reduced_data[:,0],y=reduced_data[:,1],label=songname[:],name=artists[:]) #get data and put it in a structure that bokeh can take
    source = ColumnDataSource(data=plot_data) #data
    p.circle('x', 'y', size=10, color=next(colors), source=source,legend='{}'.format(artist_trimmed))
    p.add_tools(HoverTool(tooltips=("@name: "+" @label"))) #add hover labels for each artist as we loop through, which handily makes each artists labels toggleable in the interactive plot!
    '''

#if we want each artist clustered together, do it here:
svd = TruncatedSVD(n_components=2, n_iter=7, random_state=42) #initiate SVD
#reduced_data = svd.fit_transform(all_features) #Reduce data to 2 dimensions.
reduced_data = TSNE(n_components=2, n_iter=int(sys.argv[3]), learning_rate=int(sys.argv[2])).fit_transform(all_features)


#to colour code the artists we keep track of the index with start/stop
start=0
for artist in all_data:
    data=load_obj(artist.replace('.pkl',''))
    artist_trimmed=artist.replace('_data.pkl','').replace('all_','').replace(path,'')
    stop=len(data)+start
    plot_data=OrderedDict(x=reduced_data[start:stop,0],y=reduced_data[start:stop,1],label=all_songnames[start:stop],name=all_artists[start:stop]) #get data and put it in a structure that bokeh can take
    source = ColumnDataSource(data=plot_data) #data
    p.circle('x', 'y', size=10, color=next(colors), source=source,legend='{}'.format(artist_trimmed))
    p.add_tools(HoverTool(tooltips=("@name: "+" @label"))) #add hover labels for each artist as we loop through, which handily makes each artists labels toggleable in the interactive plot!
    start=stop
    print(start)

'''
p.x_range = Range1d(-100, 9000)
'''
p.legend.label_text_font_size = '8pt'

p.legend.glyph_height = 6
p.legend.glyph_width = 6
p.legend.label_height= 2
p.legend.spacing = 0
p.legend.click_policy = "hide"

save(p)



    



