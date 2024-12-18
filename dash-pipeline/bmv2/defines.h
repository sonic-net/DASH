#ifndef _DASH_DEFINES_H_
#define _DASH_DEFINES_H_

#if defined(TABLE_HERO_SCALE)
#define TABLE_CA_TO_PA_SIZE     (8 * 1024 * 1024)
#define TABLE_ROUTING_SIZE      (4 * 1024 * 1024)

#elif defined(TABLE_BABY_HERO_SCALE)
#define TABLE_CA_TO_PA_SIZE     (8 * 1024 * 10)
#define TABLE_ROUTING_SIZE      (4 * 1024 * 10)

#else   /* default/minimum size */
#define TABLE_CA_TO_PA_SIZE     1024
#define TABLE_ROUTING_SIZE      1024

#endif


#endif /* _DASH_DEFINES_H_ */
