import React from 'react';

export default function Financials() {
  return (
    <div className="bg-white p-4 rounded shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-semibold">Financials</h2>
        <button className="text-sm text-blue-500">Details</button>
      </div>
      <div className="text-3xl text-center font-bold text-blue-600 mb-2">$7,251</div>
      <div className="text-center text-sm text-gray-500 mb-4">Goal: 10,000</div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between"><span>Housing Costs</span><span className="text-green-600">PAID</span></div>
        <div className="flex justify-between"><span>Shipping Costs</span><span className="text-red-500">UNPAID</span></div>
        <div className="flex justify-between"><span>Transportation</span><span className="text-green-600">PAID</span></div>
      </div>
      <button className="w-full mt-4 bg-blue-500 text-white py-1 rounded hover:bg-blue-600">Contribute</button>
    </div>
  );
}
