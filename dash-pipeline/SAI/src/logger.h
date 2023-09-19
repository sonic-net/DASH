#pragma once

#include <atomic>

#define DASH_LOG_ERROR(MSG, ...)       dash::Logger::getInstance().write(dash::Logger::DASH_ERROR,  "e:- %s: " MSG, __FUNCTION__, ##__VA_ARGS__)
#define DASH_LOG_WARN(MSG, ...)        dash::Logger::getInstance().write(dash::Logger::DASH_WARN,   "w:- %s: " MSG, __FUNCTION__, ##__VA_ARGS__)
#define DASH_LOG_NOTICE(MSG, ...)      dash::Logger::getInstance().write(dash::Logger::DASH_NOTICE, "n:- %s: " MSG, __FUNCTION__, ##__VA_ARGS__)
#define DASH_LOG_INFO(MSG, ...)        dash::Logger::getInstance().write(dash::Logger::DASH_INFO,   "i:- %s: " MSG, __FUNCTION__, ##__VA_ARGS__)
#define DASH_LOG_DEBUG(MSG, ...)       dash::Logger::getInstance().write(dash::Logger::DASH_DEBUG,  "d:- %s: " MSG, __FUNCTION__, ##__VA_ARGS__)

#define DASH_LOG_ENTER()               dash::Logger::ScopeLogger logger ## __LINE__ (__LINE__, __FUNCTION__)

namespace dash
{
    class Logger
    {
        public:

            // same as syslog
            enum Priority
            {
                DASH_EMERG,
                DASH_ALERT,
                DASH_CRIT,
                DASH_ERROR,
                DASH_WARN,
                DASH_NOTICE,
                DASH_INFO,
                DASH_DEBUG
            };

            static Logger &getInstance();

            static void setMinPrio(Priority prio);

            static Priority getMinPrio();

            void write(Priority prio, const char *fmt, ...)
#ifdef __GNUC__
                __attribute__ ((format (printf, 3, 4)))
#endif
                ;

            class ScopeLogger
            {
                public:

                    ScopeLogger(int line, const char *fun);
                    ~ScopeLogger();

                private:
                    const int m_line;
                    const char *m_fun;
            };

        private:

            Logger() = default;
            ~Logger() = default;

            Logger(const Logger&) = delete;
            Logger &operator=(const Logger&) = delete;

            std::atomic<Priority> m_minPrio = { DASH_NOTICE };
    };
}
