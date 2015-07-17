/*
Dev: Jonathan Ward
Last Modified: 5/12/2015
Last Modification: Added cost-based filtration.
Todo: Add Failure notification system.
*/

#include <iostream>
#include <algorithm>
#include <vector>
#include <cmath>
#include <ctime>
#include <unistd.h>

#define PI 3.141592653

using namespace std;

struct Path 
{
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

bool path_sorter(Path* const& lhs, Path* const& rhs)
{
    return lhs->cost < rhs->cost;
}

int print_pathsVect(vector<Path*>* pathsVect)
{   
    cout << pathsVect->size() << endl; 
    for(vector<Path*>::iterator path=pathsVect->begin(); path!=pathsVect->end(); ++path)
    {
        //cout << (*path)->points->size() << endl;
        cout << "Path points: ";
        for(vector<int>::iterator pt=((*path)->points)->begin(); pt!=((*path)->points)->end(); ++pt)
        {
            cout << *pt;
        }
        cout << ". Path Cost: " << (*path)->cost;
        cout << endl;
    }
    return 0;
}

vector<vector<pair<int,float>>*> generate_lattice(int latticeLength, int latticeHeight)
{
    srand (time(NULL));
    vector<vector<pair<int,float>>*> lattice;
    for(int j=0; j < latticeLength; j++)
    {
        vector<pair<int,float>>* column = new vector<pair<int,float>>(latticeHeight);    
        for(int i=0; i < column->size();i++ )
        {
            float random = float(rand() % latticeHeight + 1);	    
            (*column)[i].first = i;
            //(*column)[i].second = float(i)
            (*column)[i].second = random;
            //cout << random << " ";            
        }
        //cout << endl;
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

vector<vector<Path*>*> lattice_to_pathsForXValPairs(vector<vector<pair<int,float>>*> lattice, vector<float> angles)
{
    vector<vector<Path*>*> pathsForXValPairs;
    int offset = (angles.size() - 1)/2;
    for(vector<vector<pair<int,float>>*>::iterator it = lattice.begin(); it+1 != lattice.end(); ++it)
    {
        vector<pair<int,float>>* sliceA = *it;
        vector<pair<int,float>>* sliceB = *(it+1); 
	vector<Path*>* pathsForXValPair = new vector<Path*>;
        for(vector<pair<int,float>>::iterator i = sliceA->begin(); i != sliceA->end(); ++i)
        {
            for(vector<pair<int,float>>::iterator j = sliceB->begin(); j != sliceB->end(); ++j)
            {                            
                Path* path = new Path;
                vector<int>* points = new vector<int>;
                points->push_back(i->first);                
                points->push_back(j->first);                            
                path->points = points;
                path->cost = i->second + j->second;
                path->endpointCost = j->second;
                path->size = 2;                
                path->startYVal = i->first;
                path->endYVal = j->first;
                path->startAngle = angles[j->first - i->first + offset];
                path->endAngle = angles[j->first - i->first + offset];
                pathsForXValPair->push_back(path);                
            }
        }        
        sort(pathsForXValPair->begin(), pathsForXValPair->end(), &path_sorter);
	pathsForXValPairs.push_back(pathsForXValPair);
    }
    return pathsForXValPairs;
}

vector<Path*>* mergeFilter(vector<Path*>* paths0, vector<Path*>* paths1, float degreeConstraint, vector<float> angles, int numPaths)
{
    vector<Path*>* merged = new vector<Path*>;
    vector<Path*>* selected = new vector<Path*>;
    selected->reserve(numPaths);
    for(vector<Path*>::iterator path0 = paths0->begin(); path0 != paths0->end(); path0++)
    {
        for(vector<Path*>::iterator path1 = paths1->begin(); path1 != paths1->end(); path1++)
        {
            if( (*path0)->endYVal == (*path1)->startYVal )
            {
                if( abs((*path0)->endAngle - (*path1)->startAngle) < degreeConstraint )
                {
                    Path* mergedPath = new Path;
                    mergedPath->points = new vector<int>;
                    (mergedPath->points)->reserve((*path0)->size + (*path1)->size);
                    (mergedPath->points)->insert( (mergedPath->points)->end(),((*path0)->points)->begin(),((*path0)->points)->end()-1);
                    (mergedPath->points)->insert( (mergedPath->points)->end(),((*path1)->points)->begin(),((*path1)->points)->end());
                    mergedPath->cost = (*path0)->cost + (*path1)->cost - (*path0)->endpointCost;
                    mergedPath->endpointCost = (*path1)->endpointCost;
                    mergedPath->size = (*path0)->size + (*path1)->size - 1;
                    mergedPath->startYVal = (*path0)->startYVal;
                    mergedPath->endYVal = (*path1)->endYVal;
                    mergedPath->startAngle = (*path0)->startAngle;
                    mergedPath->endAngle = (*path1)->endAngle;
                    merged->push_back(mergedPath);
                }
            }
        }
    }
    //cout << "Unsorted: " << endl;
    //print_pathsVect(merged);
    sort(merged->begin(), merged->end(),&path_sorter);      
    //cout << "Sorted: " << endl;
    //print_pathsVect(merged);
    int selectionLength = min(int(merged->size()),numPaths); 
    selected->insert(selected->end(), merged->begin(), merged->begin()+selectionLength);
    return selected;
}


//Implements a tree fold
vector<Path*>* treefold(vector<vector<Path*>*> pathsForXValPairs, float degreeConstraint, vector<float> angles, int numPaths)
{
    vector<vector<vector<Path*>*>*> layers;	
    vector<vector<Path*>*>* workingLayer = new vector<vector<Path*>*>;
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
                vector<vector<Path*>*>* nextLayer = new vector<vector<Path*>*>;
                layers.push_back(nextLayer);                
                layersSize += 1;
            }   
            vector<Path*>* paths0 = (*layers[layersIndex])[workingLayerIndex];
            vector<Path*>* paths1 = (*layers[layersIndex])[workingLayerIndex+1];
            vector<Path*>* merged = mergeFilter(paths0,paths1,degreeConstraint,angles,numPaths);
            layers[layersIndex+1]->push_back(merged);
            workingLayerIndex += 2;
        }        
        if(breakFlag){break;}
    }
    return (*layers[layersIndex])[0];
}


int main(int argc, char** argv)
{
    int height =10;
    int length =10;
    int numPaths = 100;
    vector<vector<pair<int,float>>*> lattice = generate_lattice(length, height);
    vector<float> angles = yDelta_to_angles(height);
    vector<vector<Path*>*> pathsForXValPairs = lattice_to_pathsForXValPairs(lattice,angles);
    cout << pathsForXValPairs.size() << endl;
    float degreeConstraint = 60.0;
    //vector<Path*>* merged = mergeFilter(pathsForXValPairs[0], pathsForXValPairs[1],degreeConstraint, angles, numPaths);
    
    clock_t startTime = clock();
    vector<Path*>* goodPaths=treefold(pathsForXValPairs,degreeConstraint,angles,numPaths); 
    clock_t endTime = clock();
    clock_t clockTicks = endTime - startTime;
    double timeInSeconds = clockTicks / (double) CLOCKS_PER_SEC;
    cout << timeInSeconds << endl;
    print_pathsVect(goodPaths); 
    return 0;
}

