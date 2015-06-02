//
//  main.m
//  MapCreator
//
//  Created by Gabriel Nopper on 26/05/15.
//  Copyright (c) 2015 Gabriel Nopper. All rights reserved.
//

#import <Foundation/Foundation.h>

NSMutableArray *mainArray;

int fetchFromArray(int i, int j);
int tweakValue(int x);


/*
 /
 /  Each main function has to be uncommented to generate each type of terrain.
 /  Forest is the type builder for the hardes maps.
 /  Cliff is the mildly hard map builder.
 /  Desert build stable maps easely landable.
 /
 /  You can also use the land builder, which generates new maps with random height values, rather than type.
 /  The values in the tweak values 'if' cases is the entropy factor. The closer to 0/10000 they are, the most predictable, and therefore flat, the land is.
 /  It is IMPERATIVE that the correspondant distances of 0 and 10000 are EQUAL, otherwise you will unbalance the map. Drastically.
 /
 /  The processing time is usually around 1 or 2 seconds, the printing time usually takes from 10 to 20 seconds.
 /
 /*/


//// forestBuilder (Type)
//int main(int argc, const char * argv[]) {
//    @autoreleasepool {
//        // insert code here...
//        mainArray = [[NSMutableArray alloc] init];
//        
//        for(int i = 0; i < 2500; i++)
//            [mainArray addObject:[[NSMutableArray alloc] init]];
//        
//        
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                if(arc4random() % 10000 > 2000){
//                    [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:0]]; // Ground
//                }
//                else{
//                    if(arc4random() % 25)
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:4]]; // Tree
//                    else
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:3]]; // Water
//                }
//            }
//        
//        printf("<TerrainType xDimension='2500' zDimension='2500' type='");
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                int value = fetchFromArray(i, j);
//                printf("%d", value);
//                
//                if(j != 2499)
//                    printf(" ");
//                else
//                    printf("\n");
//            }
//        
//        printf("'/>\n");
//        NSLog(@"Hello, World!");
//    }
//    return 0;
//}


//// cliffBuilder (Type)
//int main(int argc, const char * argv[]) {
//    @autoreleasepool {
//        // insert code here...
//        mainArray = [[NSMutableArray alloc] init];
//        
//        for(int i = 0; i < 2500; i++)
//            [mainArray addObject:[[NSMutableArray alloc] init]];
//        
//        
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                if(arc4random() % 10000 > 1000){
//                    if(!arc4random()%10000)
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:20]]; // lava
//                    else
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:0]]; // ground
//                }
//                else{
//                    if(arc4random() % 4)
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:1]]; // Mud
//                    else
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:2]]; // Sand
//                }
//            }
//        
//        printf("<TerrainType xDimension='2500' zDimension='2500' type='");
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                int value = fetchFromArray(i, j);
//                printf("%d", value);
//                
//                if(j != 2499)
//                    printf(" ");
//                else
//                    printf("\n");
//            }
//        
//        printf("'/>\n");
//        NSLog(@"Hello, World!");
//    }
//    return 0;
//}

//
//// desertBuilder (Type)
//int main(int argc, const char * argv[]) {
//    @autoreleasepool {
//        // insert code here...
//        mainArray = [[NSMutableArray alloc] init];
//        
//        for(int i = 0; i < 2500; i++)
//            [mainArray addObject:[[NSMutableArray alloc] init]];
//        
//        
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                if(arc4random() % 10000)
//                    [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:2]];
//                else
//                    [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:20]];
//            }
//
//        //area 51 seed
//        
//        int area51x = arc4random() % 2500;
//        int area51z = arc4random() % 2500;
//        
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++)
//                if( 125 > sqrt( (i - area51x)*(i - area51x) + (j - area51z)*(j - area51z) )     ){
//                    
//                    [[mainArray objectAtIndex:i]replaceObjectAtIndex:j withObject:[NSNumber numberWithInt:100]];
//
//                }
//        
//        printf("<TerrainType xDimension='2500' zDimension='2500' type='");
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                int value = fetchFromArray(i, j);
//                printf("%d", value);
//                
//                if(j != 2499)
//                    printf(" ");
//                else
//                    printf("\n");
//            }
//        
//        printf("'/>\n");
//        NSLog(@"Hello, World!");
//    }
//    return 0;
//}



// Land Builder
//int main(int argc, const char * argv[]) {
//    @autoreleasepool {
//        // insert code here...
//        mainArray = [[NSMutableArray alloc] init];
//        
//        for(int i = 0; i < 2500; i++)
//            [mainArray addObject:[[NSMutableArray alloc] init]];
//        
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                if(i == 0){
//                    if(j == 0)
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:40]];
//                    else{
//                        int value = fetchFromArray(i, j - 1);
//                        value = tweakValue(value);
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:value]];
//                    }
//                }
//
//                else{
//                    
//                    if(j == 0){
//                        int value = fetchFromArray(i - 1, j);
//                        value = tweakValue(value);
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:value]];
//                    }
//                    
//                    else{
//                        int value = fetchFromArray(i - 1, j);
//                        int value2 = fetchFromArray(i, j - 1);
//                        int xvalue = (value + value2) / 2;
//                        if((value + value2) % 2 == 1){
//                            if(arc4random() % 2000 >= 1000)
//                                xvalue++;
//                        }
//                        xvalue = tweakValue(xvalue);
//                        [[mainArray objectAtIndex:i] addObject:[NSNumber numberWithInt:xvalue]];
//                    }
//                }
//            }
//        
//        for(int i = 0; i < 2500; i++)
//            for(int j = 0; j < 2500; j++){
//                int value = fetchFromArray(i, j);
//                printf("%d", value);
//                
//                if(j != 2499)
//                    printf(" ");
//                else
//                    printf("\n");
//            }
//        
//        NSLog(@"Hello, World!");
//    }
//    return 0;
//}


int fetchFromArray(int i, int j){
    return [[[mainArray objectAtIndex:i] objectAtIndex:j] intValue];
}

int tweakValue(int x){
    int value = x;
    int randomizer = arc4random() % 10000 + 1;
    
    if (randomizer <= 1250)
        value = x - 1;
    if (randomizer >= 8750)
        value = x + 1;
    if(randomizer > 9900)
        value = x + 2;
    if(randomizer < 100)
        value = x - 2;
    
    if (value > 80)
        value = 79;
    if(value <= 0)
        value = 1;
    
    return value;
}