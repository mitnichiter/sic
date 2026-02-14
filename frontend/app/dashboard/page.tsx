'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, BarChart3, MessageSquare, Thermometer, Clock } from 'lucide-react';
import { fetchClusters, Cluster } from '@/lib/api';

export default function Dashboard() {
    const [clusters, setClusters] = useState<Cluster[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const data = await fetchClusters();
            setClusters(data);
            setLoading(false);
        }
        load();
    }, []);

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                <header className="flex items-center justify-between pb-8 border-b border-white/10">
                    <div>
                        <h1 className="text-3xl font-bold">Opportunity Dashboard</h1>
                        <p className="text-neutral-400">Real-time signal from Reddit communities</p>
                    </div>
                    <Link href="/" className="text-sm font-medium opacity-50 hover:opacity-100">Back onto Home</Link>
                </header>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                        {[1, 2, 3, 4, 5, 6].map((i) => (
                            <div key={i} className="h-48 bg-white/5 rounded-2xl border border-white/10" />
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-4">
                        {/* Table Header */}
                        <div className="grid grid-cols-12 gap-4 px-6 py-3 text-sm font-medium text-neutral-500 border-b border-white/10">
                            <div className="col-span-5">Problem Cluster</div>
                            <div className="col-span-2 text-center">Score</div>
                            <div className="col-span-2 text-center">Intensity</div>
                            <div className="col-span-2 text-center">Engagement</div>
                            <div className="col-span-1"></div>
                        </div>

                        {clusters.map((cluster) => (
                            <Link
                                key={cluster.id}
                                href={`/dashboard/${cluster.id}`}
                                className="grid grid-cols-12 gap-4 px-6 py-5 items-center bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors group"
                            >
                                <div className="col-span-5">
                                    <h3 className="font-semibold text-lg truncate pr-4">{cluster.name}</h3>
                                    <p className="text-sm text-neutral-400 line-clamp-1">{cluster.description}</p>
                                </div>

                                <div className="col-span-2 flex justify-center">
                                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 font-bold">
                                        <BarChart3 className="w-4 h-4" />
                                        {Math.round(cluster.total_validation_score)}
                                    </div>
                                </div>

                                <div className="col-span-2 flex justify-center">
                                    <div className="flex items-center gap-1 text-sm text-neutral-300">
                                        <Thermometer className="w-4 h-4 text-red-400" />
                                        {Math.round(cluster.intensity_score)}%
                                    </div>
                                </div>

                                <div className="col-span-2 flex justify-center">
                                    <div className="flex items-center gap-1 text-sm text-neutral-300">
                                        <MessageSquare className="w-4 h-4 text-blue-400" />
                                        {Math.round(cluster.engagement_score)}
                                    </div>
                                </div>

                                <div className="col-span-1 flex justify-end">
                                    <ArrowRight className="w-5 h-5 text-neutral-500 group-hover:text-white transition-colors" />
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
