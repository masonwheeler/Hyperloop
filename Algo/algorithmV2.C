#include <iostream>
#include <algorithm>
#include <vector>
#include <cmath>
#include <ctime>
#include <unistd.h>
#include <map>

#define PI 3.141592653

using namespace std;

struct Path {
    vector<int>* points;
    float cost;
    float endpointCost;
    int size;
    int startXVal;
    int startYVal;
    int endYVal;
    int startAngle;
    int endAngle;
};

vector<vector<int>*> generate_lattice(int latticeLength, int latticeHeight)
{
    vector<int>* column = new vector<int>(latticeHeight);    
    iota( begin(*column), end(*column), 0);

    vector<vector<int>*> lattice;
    for(int j=0; j < latticeLength; j++)
    {
        lattice.push_back(column);
    }
    return lattice;
}

vector<float> yDelta_to_angles(int yDelta)
{
    vector<float> angles;
    for(int i=-yDelta; i <= yDelta; i++)
    {
        angles.push_back(atan2(float(i),1.0) * 180.0 / PI);
    }
    return angles;
}

vector<multimap<int,Path*>*> lattice_to_pathsForXValPairs(vector<vector<int>*> lattice, vector<float> angles)
{
    vector<multimap<int,Path*>*> pathsForXValPairs;
    int offset = (angles.size() - 1)/2;
    for(vector<vector<int>*>::iterator it = lattice.begin(); it+1 != lattice.end(); ++it)
    {
        vector<int>* sliceA = *it;
        vector<int>* sliceB = *(it+1); 
	multimap<int,Path*>* pathsForXValPair = new multimap<int,Path*>;
        for(vector<int>::iterator i = sliceA->begin(); i != sliceA->end(); ++i)
        {
            for(vector<int>::iterator j = sliceB->begin(); j != sliceB->end(); ++j)
            {                            
                Path* path = new Path;
                vector<int>* points = new vector<int>;
                points->push_back(*i);                
                points->push_back(*j);             
                path->points = points;
                path->size = 2;                
                path->startYVal = *i;
                path->endYVal = *j;
                path->startAngle = angles[*j - *i + offset];
                path->endAngle = angles[*j - *i + offset];
                pathsForXValPair->insert(pair<int,Path*>(*i,path));
            }
        }        
	pathsForXValPairs.push_back(pathsForXValPair);
    }
    return pathsForXValPairs;
}

multimap<int,Path*>* mergeFilter(multimap<int,Path*>* paths0, multimap<int,Path*>* paths1, float degreeConstraint, vector<float> angles)
{
    multimap<int,Path*>* merged = new multimap<int,Path*>;
    for(multimap<int,Path*>::iterator path0 = paths0->begin(); path0 != paths0->end(); path0++)
    {
        pair<multimap<int,Path*>::iterator, multimap<int,Path*>::iterator> matchingPaths = paths1->equal_range((path0->second)->endYVal);
        for(multimap<int,Path*>::iterator path1=matchingPaths.first; path1!=matchingPaths.second; path1++)
        {
            if( abs((path0->second)->endAngle - (path1->second)->startAngle) < degreeConstraint )
            {
                Path* mergedPath = new Path;
                mergedPath->points = new vector<int>;
                (mergedPath->points)->reserve((path0->second)->size + (path1->second)->size);
                (mergedPath->points)->insert( (mergedPath->points)->end(),((path0->second)->points)->begin(),((path0->second)->points)->end()-1);
                (mergedPath->points)->insert( (mergedPath->points)->end(),((path1->second)->points)->begin(),((path1->second)->points)->end());
                mergedPath->size = (path0->second)->size + (path1->second)->size;
                mergedPath->startYVal = (path0->second)->startYVal;
                mergedPath->endYVal = (path1->second)->endYVal;
                mergedPath->startAngle = (path0->second)->startAngle;
                mergedPath->endAngle = (path1->second)->endAngle;
                merged->insert(pair<int,Path*>((path0->second)->startYVal,mergedPath));
            }   
        }       
    }
    return merged;
}


//Implements a tree fold
multimap<int,Path*> treefold(vector<multimap<int,Path*>*> pathsForXValPairs, float degreeConstraint, vector<float> angles)
{
    vector<vector<multimap<int,Path*>*>*> layers;	
    vector<multimap<int,Path*>*>* workingLayer = new vector<multimap<int,Path*>*>;
    *workingLayer = pathsForXValPairs;
    //add the lowestLayer to the vector of layers.
    layers.push_back(workingLayer);
    //workingLayerIndex stores the position in the workingLayer
    int workingLayerIndex = 0;
    //layersIndex stores the position in the vector of layers.
    int layersIndex = 0;
    //stores the size of the vectors.
    int workingLayerSize = layers[layersIndex]->size();
    int layersSize = 1;    
    bool breakFlag = false;
    //loops until there is only one layer and that layer is completely merged.    
    while (layersSize != 1 || workingLayerSize != 1)
    {
        //evaluates how many paths are left in the working layer
        switch(workingLayerSize - workingLayerIndex)
        {  
        //in case there are no more paths left in the working layer
        case 0:
            //we want to avoid an infinite loop so if there are no layers above we break
            if( layersSize-1 == layersIndex)
            {    
                breakFlag = true;                
            }
            //otherwise we just move up one layer
            else
            {
                //increment layersIndex, i.e. move up one layer.
                ++layersIndex;                
                //update workingLayer variables
                workingLayerIndex = 0;
                workingLayerSize = layers[layersIndex]->size();
            }   
            break;	
        //in case there is only one path left in the working layer
        case 1:
            //we want to avoid an infinite loop so if there are no layers above we break
            if( layersSize-1 == layersIndex)
            {
                breakFlag = true;
            }
            //otherwise we add the path to the layer above the working layer
            else
            {
                //the layer above the working layer adds the path
                layers[layersIndex+1]->push_back((*layers[layersIndex])[workingLayerIndex]);
                //increment layersIndex, i.e. move up one layer
                ++layersIndex;
                //update workingLayer variables
                workingLayerIndex = 0;
                workingLayerSize = layers[layersIndex]->size();
            }
            break;
        //in case there are two or more paths left in working layer
        default:
            //if there are no layers above the working layer add a layer to store merges
            if ( layersSize-1 == layersIndex)
            {
                //initializes the new layer which will get destroyed as it goes out of
                // scope but the copy created by push_back will remain.
                vector<multimap<int,Path*>*>* nextLayer = new vector<multimap<int,Path*>*>;
                layers.push_back(nextLayer);                
                layersSize += 1;
            }   
            multimap<int,Path*>* paths0 = (*layers[layersIndex])[workingLayerIndex];
            multimap<int,Path*>* paths1 = (*layers[layersIndex])[workingLayerIndex+1];
            multimap<int,Path*>* merged = mergeFilter(paths0,paths1,degreeConstraint,angles);
            layers[layersIndex+1]->push_back(merged);
            workingLayerIndex += 2;
        }        
        if(breakFlag){break;}
    }
    return *(*layers[layersIndex])[0];
}


int main(int argc, char** argv)
{
    int height =3;
    int length =20;
    vector<vector<int>*> lattice = generate_lattice(length, height);
    vector<float> angles = yDelta_to_angles(height);
    vector<multimap<int,Path*>*> pathsForXValPairs = lattice_to_pathsForXValPairs(lattice,angles);
    float degreeConstraint = 60.0;
    //multimap<int,Path*>* merged = mergeFilter(pathsForXValPairs[0], pathsForXValPairs[1],degreeConstraint, angles);
    
    clock_t startTime = clock();
    multimap<int,Path*> goodPaths = treefold(pathsForXValPairs, degreeConstraint, angles); 
    clock_t endTime = clock();
    clock_t clockTicks = endTime - startTime;
    double timeInSeconds = clockTicks / (double) CLOCKS_PER_SEC;
    cout << timeInSeconds << endl;
    cout << goodPaths.size() << endl;
    return 0;
}

