'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, CheckCircle2, DollarSign, Layers, Users } from 'lucide-react';
import { fetchClusterDetails, Cluster } from '@/lib/api';

export default function ClusterDetail({ params }: { params: { id: string } }) {
    const [cluster, setCluster] = useState<Cluster | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const data = await fetchClusterDetails(parseInt(params.id));
            setCluster(data);
            setLoading(false);
        }
        load();
    }, [params.id]);

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;
    if (!cluster) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Cluster not found</div>;

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-5xl mx-auto space-y-12">
                {/* Header */}
                <header className="space-y-6">
                    <Link href="/dashboard" className="inline-flex items-center gap-2 text-sm text-neutral-400 hover:text-white transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                    </Link>

                    <div className="space-y-4">
                        <h1 className="text-4xl font-bold leading-tight">{cluster.name}</h1>
                        <p className="text-xl text-neutral-400 max-w-3xl">{cluster.description}</p>
                    </div>

                    <div className="flex gap-4">
                        <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg flex flex-col">
                            <span className="text-xs text-neutral-500 uppercase tracking-wider">Validation Score</span>
                            <span className="text-2xl font-bold text-purple-400">{Math.round(cluster.total_validation_score)}/100</span>
                        </div>
                        <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg flex flex-col">
                            <span className="text-xs text-neutral-500 uppercase tracking-wider">Frequency</span>
                            <span className="text-2xl font-bold text-white">{Math.round(cluster.frequency_score)}</span>
                        </div>
                    </div>
                </header>

                {/* Generated Ideas */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold flex items-center gap-2">
                        <CheckCircle2 className="w-6 h-6 text-green-500" />
                        Generated Solutions
                    </h2>

                    <div className="grid md:grid-cols-2 gap-6">
                        {cluster.generated_ideas.map((idea, idx) => (
                            <div key={idx} className="bg-neutral-900/50 border border-white/5 rounded-2xl p-6 hover:border-purple-500/50 transition-colors group">
                                <div className="flex justify-between items-start mb-4">
                                    <span className="px-3 py-1 bg-purple-500/10 text-purple-400 text-xs font-bold rounded-full border border-purple-500/20">
                                        {idea.solution_type}
                                    </span>
                                    <span className="text-neutral-500 text-xs font-mono">MVP Idea #{idx + 1}</span>
                                </div>

                                <h3 className="text-xl font-bold mb-3 group-hover:text-purple-300 transition-colors">{idea.title}</h3>
                                <p className="text-neutral-400 text-sm leading-relaxed mb-6">
                                    {idea.description}
                                </p>

                                <div className="space-y-3 pt-4 border-t border-white/5">
                                    <div className="flex items-center gap-3 text-sm text-neutral-300">
                                        <DollarSign className="w-4 h-4 text-green-400" />
                                        <span>{idea.monetization_strategy}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-sm text-neutral-300">
                                        <Layers className="w-4 h-4 text-blue-400" />
                                        <span>Tech: {idea.technical_complexity} Complexity</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-sm text-neutral-300">
                                        <Users className="w-4 h-4 text-orange-400" />
                                        <span>Market: {idea.market_size_estimate}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}
