'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ArrowRight, ArrowUpRight, CalendarDays, Camera, Compass, Flame,
  Home, Landmark, Leaf, MapPin, Mountain, Search, ShieldCheck, Sparkles, Trees
} from 'lucide-react';

const destinations = [
  { id:'darjeeling', name:'Darjeeling', region:'West Bengal', score:88, level:'HIGH', image:'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=85', note:'Tea estates, heritage railways and mountain views.' },
  { id:'kalimpong', name:'Kalimpong', region:'West Bengal', score:42, level:'MODERATE', image:'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=85', note:'Orchids, monasteries and quieter Himalayan ridges.' },
  { id:'lava', name:'Lava', region:'West Bengal', score:24, level:'LOW', image:'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=85', note:'Pine forests and a gateway to Neora Valley.' },
  { id:'rishop', name:'Rishop', region:'West Bengal', score:15, level:'LOW', image:'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=85', note:'Quiet ridges with expansive Kanchenjunga views.' }
];

const experiences = [
  { title:'Mountain escapes', query:'mountains', icon:Mountain, image:'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=85' },
  { title:'Forest & nature', query:'nature', icon:Trees, image:'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=900&q=85' },
  { title:'Heritage & culture', query:'culture', icon:Landmark, image:'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=900&q=85' },
  { title:'Local homestays', query:'homestays', icon:Home, image:'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=900&q=85' }
];

export default function HomePage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [date, setDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
  });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim().toLowerCase();
    if (q === 'darjeeling') router.push('/destinations/darjeeling/crowd');
    else router.push(q ? `/destinations?query=${encodeURIComponent(query.trim())}` : '/destinations');
  };

  return (
    <div className="overflow-hidden pb-0">
      <section className="relative min-h-[92svh] overflow-hidden bg-[#183A32] text-white">
        <img src="/hero-himalaya.jpg" alt="Himalayan landscape" className="absolute inset-0 h-full w-full object-cover object-center" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0d241f] via-[#102d27]/45 to-black/10" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/55 via-transparent to-transparent" />
        <div className="relative z-10 mx-auto flex min-h-[92svh] max-w-7xl flex-col justify-end px-5 pb-8 pt-32 sm:px-8 sm:pb-14 lg:px-10 lg:pb-16">
          <div className="max-w-5xl">
            <div className="reveal mb-5 flex items-center gap-2 text-[9px] font-bold uppercase tracking-[.22em] text-white/70">
              <span className="h-1.5 w-1.5 rounded-full bg-[#C98A2E]" />
              Yatri Setu · Intelligent travel
            </div>
            <h1 className="reveal reveal-delay-1 font-editorial text-[4.4rem] leading-[.78] tracking-[-.045em] sm:text-[6.8rem] lg:text-[8.8rem]">
              Travel beyond<br /><em>the obvious.</em>
            </h1>
            <p className="reveal reveal-delay-2 mt-7 max-w-xl text-sm leading-6 text-white/75 sm:text-base">
              Discover quieter places, stay local and travel with better information — before the crowds decide your route.
            </p>

            <form onSubmit={submit} className="reveal reveal-delay-3 mt-8 grid max-w-4xl gap-2 rounded-[22px] border border-white/15 bg-white/[.94] p-2 text-[#171714] shadow-2xl backdrop-blur-xl sm:grid-cols-[1.5fr_1fr_auto]">
              <label className="flex items-center gap-3 rounded-2xl px-4 py-3 hover:bg-black/[.03]">
                <Search className="h-4 w-4 text-[#183A32]" />
                <span className="min-w-0 flex-1">
                  <span className="block text-[9px] font-bold uppercase tracking-[.15em] text-black/40">Where</span>
                  <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search a destination" className="mt-0.5 w-full bg-transparent text-sm font-semibold outline-none placeholder:text-black/35" />
                </span>
              </label>
              <label className="flex items-center gap-3 rounded-2xl px-4 py-3 hover:bg-black/[.03]">
                <CalendarDays className="h-4 w-4 text-[#183A32]" />
                <span className="min-w-0 flex-1">
                  <span className="block text-[9px] font-bold uppercase tracking-[.15em] text-black/40">When</span>
                  <input type="date" value={date} onChange={e=>setDate(e.target.value)} min={new Date().toISOString().split('T')[0]} className="mt-0.5 w-full bg-transparent text-sm font-semibold outline-none" />
                </span>
              </label>
              <button className="flex min-h-14 items-center justify-center gap-2 rounded-[18px] bg-[#183A32] px-7 text-xs font-bold text-white transition hover:-translate-y-0.5 hover:bg-[#214B41]">
                Explore <ArrowRight className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </section>

      <section className="bg-[#183A32] px-5 py-20 text-white sm:px-8 sm:py-28 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
            <div>
              <div className="mb-3 text-[9px] font-bold uppercase tracking-[.22em] text-white/45">Travel intelligence</div>
              <h2 className="font-editorial text-5xl leading-none sm:text-6xl">Know before you go.</h2>
            </div>
            <Link href="/destinations/darjeeling/crowd" className="text-xs font-bold text-white/65 transition hover:text-white">View crowd intelligence <ArrowUpRight className="ml-1 inline h-3.5 w-3.5" /></Link>
          </div>
          <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {destinations.map((d,i)=>(
              <Link key={d.id} href={`/destinations/${d.id}/crowd`} className="group rounded-[20px] border border-white/10 bg-white/[.06] p-5 transition duration-500 hover:-translate-y-1 hover:bg-white/[.1]">
                <div className="flex items-center justify-between text-[9px] font-bold uppercase tracking-[.15em] text-white/45"><span>{d.region}</span><span>{String(i+1).padStart(2,'0')}</span></div>
                <div className="mt-7 flex items-end justify-between">
                  <div><div className="text-lg font-semibold">{d.name}</div><div className="mt-1 text-[10px] text-white/45">{d.level} crowd</div></div>
                  <div className="font-editorial text-5xl leading-none">{d.score}<span className="font-sans text-[10px] text-white/40">/100</span></div>
                </div>
                <div className="mt-5 h-px bg-white/10"><div className="h-px bg-[#C98A2E]" style={{width:`${d.score}%`}} /></div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-5 py-20 sm:px-8 sm:py-28 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <div className="text-[9px] font-bold uppercase tracking-[.22em] text-black/40">Discover differently</div>
            <h2 className="mt-3 font-editorial text-5xl leading-[.9] tracking-tight sm:text-7xl">The places you<br /><em>weren't looking for.</em></h2>
          </div>
          <div className="mt-12 grid gap-4 md:grid-cols-12">
            {destinations.map((d,i)=>(
              <Link key={d.id} href={`/destinations/${d.id}`} className={`group relative overflow-hidden rounded-[24px] ${i===0?'md:col-span-7 md:row-span-2':''} ${i===1?'md:col-span-5':''} ${i>1?'md:col-span-5':''} min-h-[330px]`}>
                <img src={d.image} alt={d.name} className="absolute inset-0 h-full w-full object-cover transition duration-700 ease-out group-hover:scale-[1.04]" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/15 to-transparent" />
                <div className="absolute inset-x-0 bottom-0 p-6 text-white sm:p-7">
                  <div className="mb-2 flex items-center gap-2 text-[9px] font-bold uppercase tracking-[.18em] text-white/60"><MapPin className="h-3 w-3" />{d.region}</div>
                  <div className="flex items-end justify-between gap-4"><div><h3 className="font-editorial text-4xl leading-none">{d.name}</h3><p className="mt-2 max-w-md text-xs text-white/65">{d.note}</p></div><ArrowUpRight className="h-5 w-5 shrink-0 opacity-0 transition group-hover:opacity-100" /></div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#E7EEE9] px-5 py-20 sm:px-8 sm:py-28 lg:px-10">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[.85fr_1.15fr] lg:items-center">
          <div>
            <div className="text-[9px] font-bold uppercase tracking-[.22em] text-[#183A32]/50">A quieter way to travel</div>
            <h2 className="mt-3 font-editorial text-5xl leading-[.9] sm:text-7xl">When one place gets crowded,<br /><em>discover another way.</em></h2>
            <p className="mt-6 max-w-lg text-sm leading-6 text-black/55">Yatri Setu compares travel pressure and destination similarity so you can discover alternatives without losing the character of the trip you wanted.</p>
            <Link href="/destinations/darjeeling/alternatives" className="premium-button mt-8">Find a quieter alternative <ArrowRight className="ml-2 h-4 w-4" /></Link>
          </div>
          <div className="rounded-[28px] bg-[#FCFAF6] p-4 shadow-[0_20px_60px_rgba(23,23,20,.08)] sm:p-6">
            <div className="grid gap-4 sm:grid-cols-[1fr_auto_1fr] sm:items-center">
              <div className="rounded-[20px] bg-black/[.03] p-6"><div className="text-[9px] font-bold uppercase tracking-[.18em] text-black/35">Current choice</div><div className="mt-5 font-editorial text-4xl">Darjeeling</div><div className="mt-2 text-xs text-black/45">88 / 100 · High crowd</div></div>
              <div className="text-center"><div className="font-editorial text-4xl text-[#183A32]">87%</div><div className="text-[8px] font-bold uppercase tracking-[.15em] text-black/35">similarity</div></div>
              <div className="rounded-[20px] bg-[#E7EEE9] p-6"><div className="text-[9px] font-bold uppercase tracking-[.18em] text-[#183A32]/55">Alternative</div><div className="mt-5 font-editorial text-4xl">Kalimpong</div><div className="mt-2 text-xs text-black/45">42 / 100 · Moderate crowd</div></div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-5 py-20 sm:px-8 sm:py-28 lg:px-10">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div><div className="text-[9px] font-bold uppercase tracking-[.22em] text-black/40">Curated experiences</div><h2 className="mt-2 font-editorial text-5xl leading-none sm:text-6xl">Travel with a little more meaning.</h2></div>
            <Link href="/destinations" className="text-xs font-bold text-black/50 hover:text-black">Explore all <ArrowRight className="ml-1 inline h-3.5 w-3.5" /></Link>
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {experiences.map(e=>{const Icon=e.icon; return <Link key={e.title} href={`/destinations?query=${e.query}`} className="group">
              <div className="relative aspect-[4/5] overflow-hidden rounded-[24px]"><img src={e.image} alt={e.title} className="h-full w-full object-cover transition duration-700 group-hover:scale-[1.04]" /><div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" /><div className="absolute inset-x-0 bottom-0 p-5 text-white"><Icon className="mb-8 h-5 w-5 text-[#C98A2E]" /><h3 className="font-editorial text-3xl leading-none">{e.title}</h3></div></div>
            </Link>})}
          </div>
        </div>
      </section>

      <section className="bg-[#F5F2EA] px-5 pb-24 sm:px-8 sm:pb-32 lg:px-10">
        <div className="mx-auto grid max-w-7xl overflow-hidden rounded-[28px] bg-[#183A32] lg:grid-cols-[1.15fr_.85fr]">
          <div className="p-8 text-white sm:p-12 lg:p-16">
            <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[.2em] text-white/45"><Leaf className="h-3.5 w-3.5 text-[#C98A2E]" /> Responsible travel</div>
            <h2 className="mt-5 max-w-xl font-editorial text-5xl leading-[.9] sm:text-7xl">Your next journey can mean more.</h2>
            <p className="mt-6 max-w-lg text-sm leading-6 text-white/55">Choose local stays, quieter destinations and off-peak journeys. Earn Green Credits and use them as discounts on your next Yatri Setu booking.</p>
            <div className="mt-8 flex flex-wrap gap-3"><Link href="/homestays" className="premium-button bg-white text-[#183A32] hover:bg-white">Stay local <Home className="ml-2 h-4 w-4" /></Link><Link href="/dashboard" className="rounded-full border border-white/15 px-6 py-3 text-xs font-bold text-white transition hover:bg-white/10">View Green Credits</Link></div>
          </div>
          <div className="relative min-h-[300px] overflow-hidden lg:min-h-0"><img src="https://images.unsplash.com/photo-1528181304800-259b08848526?auto=format&fit=crop&w=1200&q=85" alt="Quiet Himalayan village" className="absolute inset-0 h-full w-full object-cover" /><div className="absolute inset-0 bg-gradient-to-r from-[#183A32] via-[#183A32]/25 to-transparent" /></div>
        </div>
      </section>
    </div>
  );
}
