const mongoose = require('mongoose');
const Event = require('../src/models/Event');
const Registration = require('../src/models/Registration');

const seedData = async () => {
  try {
    await mongoose.connect('mongodb://localhost:27017/eventdb', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    await Event.deleteMany({});
    await Registration.deleteMany({});

    const events = [
      {
        title: 'Tech Conference 2024',
        description: 'A premier gathering of tech innovators and developers.',
        date: new Date('2024-06-15T10:00:00Z'),
        location: 'San Francisco, CA',
        capacity: 500,
        organizer: 'TechCorp',
        category: 'Technology',
      },
      {
        title: 'Music Festival',
        description: 'Live performances from top artists across genres.',
        date: new Date('2024-07-20T18:00:00Z'),
        location: 'Austin, TX',
        capacity: 1000,
        organizer: 'SoundEvents Inc.',
        category: 'Music',
      },
      {
        title: 'Food & Wine Expo',
        description: 'Taste the finest wines and cuisines from around the world.',
        date: new Date('2024-08-10T12:00:00Z'),
        location: 'Napa Valley, CA',
        capacity: 300,
        organizer: 'Gourmet Events',
        category: 'Food & Drink',
      },
    ];

    const createdEvents = await Event.insertMany(events);

    const registrations = [
      {
        eventId: createdEvents[0]._id,
        attendeeName: 'Alice Johnson',
        email: 'alice.johnson@example.com',
        phone: '+1-415-555-0123',
        ticketType: 'VIP',
        status: 'confirmed',
      },
      {
        eventId: createdEvents[0]._id,
        attendeeName: 'Bob Smith',
        email: 'bob.smith@example.com',
        phone: '+1-415-555-0124',
        ticketType: 'General',
        status: 'confirmed',
      },
      {
        eventId: createdEvents[1]._id,
        attendeeName: 'Carol Davis',
        email: 'carol.davis@example.com',
        phone: '+1-512-555-0125',
        ticketType: 'General',
        status: 'pending',
      },
      {
        eventId: createdEvents[2]._id,
        attendeeName: 'David Wilson',
        email: 'david.wilson@example.com',
        phone: '+1-707-555-0126',
        ticketType: 'Premium',
        status: 'confirmed',
      },
    ];

    await Registration.insertMany(registrations);

    console.log('✅ Seed data successfully loaded.');
    mongoose.connection.close();
  } catch (error) {
    console.error('❌ Error seeding data:', error.message);
    process.exit(1);
  }
};

seedData();