#include "logger.h"

#include <stdarg.h>
#include <stdio.h>
#include <syslog.h>

using namespace dash;

Logger &Logger::getInstance()
{
    static Logger m_logger;

    return m_logger;
}

void Logger::setMinPrio(Priority prio)
{
    getInstance().m_minPrio = prio;
}

Logger::Priority Logger::getMinPrio()
{
    return getInstance().m_minPrio;
}

void Logger::write(Priority prio, const char *fmt, ...)
{
    if (prio > m_minPrio)
        return;

    // print to syslog
    {
        va_list ap;
        va_start(ap, fmt);

        vsyslog(prio, fmt, ap);

        va_end(ap);
    }

    // print to stderr
    {
        va_list ap;
        va_start(ap, fmt);

        vfprintf(stderr, fmt, ap);
        fprintf(stderr, "\n");

        va_end(ap);
    }
}

Logger::ScopeLogger::ScopeLogger(int line, const char *fun) : m_line(line), m_fun(fun)
{
    dash::Logger::getInstance().write(dash::Logger::DASH_DEBUG, "d:> %s: enter", m_fun);
}

Logger::ScopeLogger::~ScopeLogger()
{
    dash::Logger::getInstance().write(dash::Logger::DASH_DEBUG, "d:< %s: exit", m_fun);
}
