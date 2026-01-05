'use client'

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, Activity, Server, Clock } from 'lucide-react'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import type { HealthResponse, APIInfo } from '@/lib/api'

export default function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [apiInfo, setApiInfo] = useState<APIInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const [healthData, rootData] = await Promise.all([
          apiClient.healthCheck().catch(() => null),
          apiClient.getRoot().catch(() => null),
        ])

        if (healthData) {
          setHealth(healthData)
        }
        if (rootData) {
          setApiInfo(rootData)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const isHealthy = health?.status === 'healthy'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-blue-950 to-purple-950">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4">
        <div className="text-white font-bold tracking-wider">
          {{cookiecutter.project_name}}
        </div>
        <div className="flex items-center space-x-4">
          <a
            href={apiInfo?.docs_url || '/docs'}
            target="_blank"
            rel="noopener noreferrer"
            className="text-white/80 hover:text-white transition-colors"
          >
            API Docs
          </a>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-blue-500 bg-clip-text text-transparent mb-6"
          >
            {{cookiecutter.project_name}}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl text-white/80 mb-8 max-w-2xl mx-auto"
          >
            {{cookiecutter.description}}
          </motion.p>
        </div>

        {/* Health Status Card */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="max-w-4xl mx-auto mb-12"
        >
          <div className="bg-gray-900/50 rounded-lg border border-gray-700/50 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center space-x-3">
                {loading ? (
                  <>
                    <Activity className="w-6 h-6 animate-pulse" />
                    <span>Checking Status...</span>
                  </>
                ) : isHealthy ? (
                  <>
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                    <span>System Healthy</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-6 h-6 text-red-500" />
                    <span>System Unhealthy</span>
                  </>
                )}
              </h2>
              {health && (
                <div className="text-white/60 text-sm flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>
                    {new Date(health.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>

            {error && (
              <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {health && (
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-800/50 rounded-lg">
                  <div className="text-white/60 text-sm mb-2">Service</div>
                  <div className="text-white font-semibold">{health.service}</div>
                </div>
                {health.version && (
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <div className="text-white/60 text-sm mb-2">Version</div>
                    <div className="text-white font-semibold">{health.version}</div>
                  </div>
                )}
                {health.environment && (
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <div className="text-white/60 text-sm mb-2">Environment</div>
                    <div className="text-white font-semibold capitalize">
                      {health.environment}
                    </div>
                  </div>
                )}
                {health.services && (
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <div className="text-white/60 text-sm mb-2">Services</div>
                    <div className="space-y-1">
                      {Object.entries(health.services).map(([key, value]) => (
                        <div key={key} className="flex items-center space-x-2">
                          <Server className="w-3 h-3 text-white/40" />
                          <span className="text-white text-sm">
                            {key}:{' '}
                            <span
                              className={
                                value === 'healthy'
                                  ? 'text-green-400'
                                  : 'text-red-400'
                              }
                            >
                              {value}
                            </span>
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {apiInfo && (
              <div className="mt-6 pt-6 border-t border-gray-700/50">
                <div className="text-white/60 text-sm mb-2">API Information</div>
                <div className="text-white">
                  <p className="mb-2">{apiInfo.description}</p>
                  <div className="flex flex-wrap gap-4 text-sm">
                    <a
                      href={apiInfo.docs_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:text-purple-300 transition-colors"
                    >
                      View API Docs →
                    </a>
                    <a
                      href={apiInfo.health_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      Health Check →
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="grid md:grid-cols-3 gap-8"
        >
          {/* FastAPI Backend */}
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Server className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">FastAPI Backend</h3>
            <p className="text-white/70 leading-relaxed">
              Modern, high-performance API built with FastAPI and async Python
            </p>
          </div>

          {/* LangChain Integration */}
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Activity className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">LangChain Integration</h3>
            <p className="text-white/70 leading-relaxed">
              LLM integration with OpenRouter and agent framework support
            </p>
          </div>

          {/* Clerk Authentication */}
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">Secure Auth</h3>
            <p className="text-white/70 leading-relaxed">
              Enterprise-grade authentication with Clerk integration
            </p>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="text-center py-8 text-white/40 text-sm">
        © 2025 {{cookiecutter.project_name}}. All rights reserved.
      </footer>
    </div>
  )
}
