import React from 'react';

export default function UserWidgets({ users }) {
  if (!users.length) return <p>No users to show.</p>;
  return (
    <div className="widget-list">
      {users.map(u => (
        <div key={u.id} className="widget-card">
          <img src={u.profileUrl} alt="profile" />
          <h4>{u.name}</h4>
          <p><em>{u.designation}</em></p>
          <p>Rights: {u.rights.join(', ')}</p>
        </div>
      ))}
    </div>
  );
}
