import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { CloudRain, Sun, Cloud, CloudLightning, CloudSnow, Wind } from 'lucide-react';

const WeatherResultCard = ({ prediction }) => {
  // Weather descriptions and icons mapping
  const weatherInfo = {
    dew: {
      icon: <Cloud className="w-8 h-8 text-blue-400" />,
      description: "Tiny water droplets have formed on surfaces due to condensation. This typically occurs in the early morning when the air cools.",
      tips: "Perfect conditions for early morning photography. Watch out for slippery surfaces."
    },
    fogsmog: {
      icon: <Cloud className="w-8 h-8 text-gray-400" />,
      description: "Reduced visibility due to condensed water vapor (fog) or pollution (smog) in the air.",
      tips: "Drive carefully and use fog lights. If smog, consider wearing a mask and limiting outdoor activities."
    },
    frost: {
      icon: <CloudSnow className="w-8 h-8 text-blue-200" />,
      description: "A thin layer of ice crystals has formed on surfaces when temperatures drop below freezing.",
      tips: "Protect sensitive plants. Be cautious of slippery surfaces, especially in the early morning."
    },
    glaze: {
      icon: <CloudSnow className="w-8 h-8 text-blue-300" />,
      description: "A smooth coating of ice formed when freezing rain or drizzle hits cold surfaces.",
      tips: "Extremely slippery conditions. Take extra care while walking or driving."
    },
    hail: {
      icon: <CloudSnow className="w-8 h-8 text-gray-600" />,
      description: "Solid precipitation in the form of balls or lumps of ice.",
      tips: "Seek shelter immediately. Protect vehicles and outdoor equipment if possible."
    },
    lightning: {
      icon: <CloudLightning className="w-8 h-8 text-yellow-500" />,
      description: "Electrical discharge in the atmosphere, typically during thunderstorms.",
      tips: "Stay indoors. Avoid open areas and tall objects. Unplug electronic devices."
    },
    rain: {
      icon: <CloudRain className="w-8 h-8 text-blue-500" />,
      description: "Precipitation in the form of water drops falling from clouds.",
      tips: "Carry an umbrella. Be prepared for wet conditions and reduced visibility while driving."
    },
    rainbow: {
      icon: <Sun className="w-8 h-8 text-yellow-400" />,
      description: "An optical phenomenon occurring when sunlight is reflected and refracted by water droplets.",
      tips: "Great photo opportunity! Look in the direction opposite to the sun for the best view."
    },
    rime: {
      icon: <CloudSnow className="w-8 h-8 text-white" />,
      description: "A white ice deposit formed when supercooled water droplets freeze upon impact with surfaces.",
      tips: "Beautiful for photography but can be dangerous on roads and power lines."
    },
    sandstorm: {
      icon: <Wind className="w-8 h-8 text-orange-400" />,
      description: "Strong winds carrying large amounts of sand and dust through the air.",
      tips: "Stay indoors. Wear protective gear if you must go out. Keep windows and doors closed."
    },
    snow: {
      icon: <CloudSnow className="w-8 h-8 text-blue-100" />,
      description: "Precipitation in the form of small ice crystals.",
      tips: "Dress warmly in layers. Be careful of slippery conditions. Allow extra time for travel."
    }
  };

  if (!prediction || !prediction.predicted_class) {
    return null;
  }

  const weather = weatherInfo[prediction.predicted_class.toLowerCase()];
  const confidencePercent = (prediction.prediction * 100).toFixed(1);

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {weather.icon}
          <span className="capitalize">{prediction.predicted_class} Detected</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Confidence:</span>
            <div className="flex items-center gap-2">
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
              <span className="text-sm">{confidencePercent}%</span>
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="font-medium">Description:</h3>
            <p className="text-sm text-gray-600">{weather.description}</p>
          </div>

          <div className="space-y-2">
            <h3 className="font-medium">Tips:</h3>
            <p className="text-sm text-gray-600">{weather.tips}</p>
          </div>

          {prediction.top_predictions && (
            <div className="space-y-2">
              <h3 className="font-medium">Other Possibilities:</h3>
              <div className="space-y-1">
                {prediction.top_predictions.slice(1).map((pred, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="capitalize">{pred.class}</span>
                    <span>{pred.percentage.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default WeatherResultCard;