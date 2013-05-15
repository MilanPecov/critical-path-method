# coding=utf-8

import os

import webapp2
import jinja2
import urllib

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
graph={}

#--------------/ Functions --------------

def render_str(template, **params):
    """
    * Loads templates from the "templates" folder
    """
    t = jinja_env.get_template(template)
    return t.render(params)

def find_all_paths(graph, start, end, path=[],cost=0):
    """
    * Takes a graph and the start and end nodes as arguments
      graph : key = 'node'; value = [['edge1','edge2,...'],[weight1,weight2,...]]

    * Returns a list of all paths between start and end node (without cycles)
      [['node1','node2','...','cost1'],['node1','node3','...','cost2'],...]
    """
    path = path + [start]
    cost = cost
    if start == end:
        return [path+[cost]]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start][0]:
        if node not in path:
            index=graph[start][0].index(node)
            cost += int(graph[start][1][index])
            newpaths = find_all_paths(graph, node, end, path, cost)
            for newpath in newpaths:
                paths.append(newpath)
                cost=0
    return paths

def critical_path(paths):
    """
    * Takes list of lists(paths)

    * Returns critical path(string) and his cost(int)
    """
    paths.sort(key=lambda x: int(x[-1]))
    critical = paths[-1]
    cost = critical.pop()
    return ("->").join(critical), cost


#--------------/ Base Class ------------

class DataHandler(webapp2.RequestHandler):
    """
    * Rendering functions
    """
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
    def render_str(self, template, **params):
        return render_str(template, **params)
    def render(self,template,**kw):
        """
        * Takes template name, additional keywords, and produces html output
        """
        self.write(self.render_str(template, **kw))
   
  
#--------------/ Main -----------------

class MainPage(DataHandler):
    def get(self):
        if self.request.get('rows'):    
            rows=self.request.get('rows')
        else:
            rows=3 #default
        self.render('base.html', rows=int(rows))

    def post(self):
        if self.request.get('rows'): # change the number of rows
            rows = str(self.request.get('rows'))
            self.redirect('/?rows=' + rows)

        #TODO: If VALID
        if self.request.get('n1'):
            i=0
            graph = {} 
            #html names | nodes: n1,n2,...; ends: e1,e2...; weights: w1,w2,....
            while(self.request.get('n%s' %i)):
                node=str(self.request.get('n%s' %i))   #node row i
                if self.request.get('e%s' %i): 
                    edge=str(self.request.get('e%s' %i)) #end row i
                else:
                    edge = '' #no end
                if self.request.get('w%s' %i):
                    weight=str(self.request.get('w%s' %i)) #weight row i
                else:
                    weight = '' #no weight
                if node not in graph.keys():
                    graph[node]=[[edge],[weight]]
                elif node in graph.keys():
                    edge_list = graph.get(node)[0]
                    edge_list.append(edge)
                    weight_list = graph.get(node)[1]
                    weight_list.append(weight)
                    graph[node]=[edge_list,weight_list]
                i=i+1

            start = self.request.get('node1')
            end = self.request.get('node2')
            paths = find_all_paths(graph,start,end)
            critical,cost = critical_path(paths)
            self.render('base.html', rows = len(graph.keys()), graph=graph, path=critical,cost=cost)   

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/(.*)', MainPage)],
                              debug=True)