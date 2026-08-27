import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

interface AssetSearchProps {
  initialValue?: string;
  onSearch: (value: string) => void;
}

export const AssetSearch: React.FC<AssetSearchProps> = ({ initialValue = '', onSearch }) => {
  const [value, setValue] = useState(initialValue);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(value);
    }, 500);

    return () => clearTimeout(timer);
  }, [value, onSearch]);

  return (
    <div className="relative w-full md:w-96">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search size={18} className="text-slate-400" />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2 border border-slate-700 rounded-lg leading-5 bg-slate-900 text-slate-300 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-colors"
        placeholder="Search assets, hosts, owners..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
};
