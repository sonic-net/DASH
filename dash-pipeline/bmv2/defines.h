#ifndef _DASH_DEFINES_H_
#define _DASH_DEFINES_H_

#ifdef TABLE_FULL_SCALE
#define TABLE_CA_TO_PA_SIZE     (8 * 1024 * 1024)
#define TABLE_ROUTING_SIZE      (4 * 1024 * 1024)

#else   /* default size */
#define TABLE_CA_TO_PA_SIZE     (8 * 1024)
#define TABLE_ROUTING_SIZE      (4 * 1024)

#endif


#endif /* _DASH_DEFINES_H_ */
